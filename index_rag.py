import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from product.models import Product
import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from django.utils.html import strip_tags
import html

def index_products():
    client = chromadb.PersistentClient(path="./chroma_db")
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(name="products", embedding_function=default_ef)
    products = Product.objects.filter(status='True')
    
    documents = []
    metadatas = []
    ids = []
    
    for p in products:
        # Làm sạch HTML và thực thể HTML (như &ocirc;)
        clean_desc = html.unescape(strip_tags(p.description)) if p.description else ""
        clean_detail = html.unescape(strip_tags(p.detail)) if p.detail else ""
        
        content = f"Sản phẩm: {p.title}. Giá: {int(p.price):,} VND. Mô tả: {clean_desc}. Thông số kỹ thuật/Chi tiết: {clean_detail}. Danh mục: {p.category.title}"
        documents.append(content)
        metadatas.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "slug": p.slug,
            "image": p.image.url if p.image else "/static/img/product01.jpg"
        })
        ids.append(str(p.id))
        
    if ids:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Đã cập nhật {len(ids)} sản phẩm vào Vector DB thành công!")
    else:
        print("Không có sản phẩm nào để index.")

if __name__ == "__main__":
    index_products()
