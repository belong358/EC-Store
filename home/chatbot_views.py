import json
import re
import chromadb
from chromadb.utils import embedding_functions
from google import genai

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings



_client = genai.Client(api_key=settings.GEMINI_API_KEY)
# Tên model AI — để trong settings/.env vì Google định kỳ khai tử các model cũ
# (VD gemini-2.0-flash-lite đã bị shutdown hoàn toàn từ 01/06/2026). Khi Google
# thông báo khai tử model đang dùng, chỉ cần đổi GEMINI_MODEL trong .env,
# không cần sửa code.
_GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-3.1-flash-lite")

_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_default_ef = embedding_functions.DefaultEmbeddingFunction()
_collection = _chroma_client.get_or_create_collection(
    name="products",
    embedding_function=_default_ef,
)


def extract_intent(user_message: str, history: list[dict]) -> dict:
    """
    Trả về dict:
    {
        "needs_product": bool,
        "product_type": str | null,   # "laptop", "tai nghe", ...
        "budget": int | null,          # đơn vị VND
        "search_query": str            # câu query tối ưu để tìm vector DB
    }
    """
    history_text = ""
    if history:
        last_turns = history[-4:]  # giữ 2 lượt gần nhất
        history_text = "\n".join(
            f"{'Khách' if m['role'] == 'user' else 'Bot'}: {m['content']}"
            for m in last_turns
        )

    prompt = f"""Phân tích đoạn hội thoại sau và trích xuất thông tin.

Lịch sử hội thoại (có thể rỗng):
{history_text if history_text else "(chưa có)"}

Tin nhắn mới nhất của khách: {user_message}

Trả về JSON thuần (không markdown, không giải thích) theo đúng cấu trúc:
{{
  "needs_product": true/false,
  "product_type": "tên loại sản phẩm hoặc null",
  "budget": số nguyên VND hoặc null,
  "search_query": "câu query ngắn gọn bằng tiếng Việt để tìm sản phẩm phù hợp"
}}

Quy tắc:
- needs_product = true nếu khách muốn mua, hỏi giá, xem, tư vấn, gợi ý sản phẩm
- budget: chuyển đổi về VND (5 triệu → 5000000, 500k → 500000)
- search_query: viết lại súc tích, bỏ từ thừa, thêm context từ lịch sử nếu cần
- Nếu không liên quan đến sản phẩm, needs_product = false và search_query = ""
"""

    try:
        resp = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        raw = resp.text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        return json.loads(raw)
    except Exception as e:
        print(f"=== [CHATBOT] Lỗi extract_intent ({type(e).__name__}): {e} ===")
        return {
            "needs_product": False,
            "product_type": None,
            "budget": None,
            "search_query": user_message,
        }


def search_products(intent: dict, max_cards: int = 3) -> tuple[list[dict], list[str]]:
    """Trả về (product_cards, context_docs)"""
    if not intent.get("needs_product") or not intent.get("search_query"):
        return [], []

    budget = intent.get("budget")
    product_type = (intent.get("product_type") or "").lower()
    query = intent["search_query"]

    where_filter = None
    if budget:
        where_filter = {"price": {"$lte": int(budget * 1.15)}}  # dư 15% để không quá cứng

    try:
        results = _collection.query(
            query_texts=[query],
            n_results=50,
            where=where_filter,
        )
    except Exception:
        return [], []

    candidates = []
    docs_raw = results.get("documents", [[]])[0]
    metas_raw = results.get("metadatas", [[]])[0]

    for doc, meta in zip(docs_raw, metas_raw):
        price = float(meta.get("price", 0))
        title = (meta.get("title") or "").lower()

        # Lọc theo budget chặt hơn
        if budget and price > budget * 1.15:
            continue

        # Lọc theo loại sản phẩm nếu có
        if product_type and product_type not in title and product_type not in doc.lower():
            continue

        candidates.append(
            {
                "id": meta.get("id"),
                "title": meta.get("title"),
                "price": price,
                "display_price": "{:,.0f} VND".format(price).replace(",", "."),
                "image": meta.get("image", "/static/img/product01.jpg"),
                "slug": meta.get("slug"),
                "doc": doc,
            }
        )

    if budget:
        candidates.sort(key=lambda x: x["price"], reverse=True)

    product_cards = []
    context_docs = []
    for c in candidates[:max_cards]:
        product_cards.append(
            {
                "id": c["id"],
                "title": c["title"],
                "price": c["display_price"],
                "image": c["image"],
                "slug": c["slug"],
            }
        )
        context_docs.append(c["doc"])

    return product_cards, context_docs


def generate_reply(
    user_message: str,
    history: list[dict],
    intent: dict,
    context_docs: list[str],
) -> str:
    budget = intent.get("budget")
    budget_str = "{:,.0f} VND".format(budget).replace(",", ".") if budget else "Không rõ"
    context_str = (
        "\n".join(f"- {d}" for d in context_docs)
        if context_docs
        else "KHÔNG CÓ SẢN PHẨM PHÙ HỢP TRONG KHO."
    )

    history_text = ""
    if history:
        last_turns = history[-6:]
        history_text = "\n".join(
            f"{'Khách' if m['role'] == 'user' else 'Bot'}: {m['content']}"
            for m in last_turns
        )

    prompt = f"""Bạn là EleStore AI – chuyên gia tư vấn công nghệ thân thiện, am hiểu sản phẩm.

=== LỊCH SỬ HỘI THOẠI ===
{history_text if history_text else "(Đây là tin nhắn đầu tiên)"}

=== TIN NHẮN MỚI ===
Khách: {user_message}
Ngân sách: {budget_str}

=== DỮ LIỆU SẢN PHẨM TỪ KHO ===
{context_str}

=== QUY TẮC ===
1. Trả lời tự nhiên, thân thiện, đúng trọng tâm. Không cần quá ngắn nếu khách cần giải thích.
2. Chỉ giới thiệu sản phẩm có trong danh sách kho ở trên. KHÔNG bịa sản phẩm.
3. Nếu kho báo "KHÔNG CÓ SẢN PHẨM PHÙ HỢP", thông báo lịch sự và gợi ý điều chỉnh ngân sách hoặc yêu cầu.
4. Nếu câu hỏi không liên quan sản phẩm (chào hỏi, hỏi chung...), trả lời bình thường như trợ lý thân thiện.
5. Nhớ ngữ cảnh từ lịch sử hội thoại – không hỏi lại thứ khách đã nói.
6. Trả lời bằng tiếng Việt.
"""

    try:
        response = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print("=== [CHATBOT] Lỗi gọi Gemini API ===")
        print(f"Model: {_GEMINI_MODEL}")
        print(f"Loại lỗi: {type(e).__name__}")
        print(f"Chi tiết: {e}")
        print("=====================================")
        return (
            "Xin lỗi, hệ thống AI đang tạm thời gián đoạn (có thể do model AI đã thay đổi/hết hạn phía nhà cung cấp). "
            "Bạn vui lòng thử lại sau ít phút, hoặc liên hệ trực tiếp qua mục Liên hệ để được hỗ trợ nhé!"
        )


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = (data.get("message") or "").strip()
        history: list[dict] = data.get("history", [])

        if not user_message:
            return JsonResponse({"error": "Message is empty"}, status=400)

        intent = extract_intent(user_message, history)

        is_general = any(
            k in user_message.lower()
            for k in ["gợi ý", "tư vấn", "danh sách", "các", "những", "mẫu nào", "nào tốt"]
        )
        max_cards = 3 if (is_general or intent.get("budget")) else 1

        product_cards, context_docs = search_products(intent, max_cards=max_cards)

        ai_message = generate_reply(user_message, history, intent, context_docs)

        return JsonResponse({"reply": ai_message, "products": product_cards})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)