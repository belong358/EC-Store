import hashlib
import hmac
import json
import requests
import uuid

class MoMoPayment:
    def __init__(self, partner_code, access_key, secret_key, endpoint):
        self.partner_code = partner_code
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint

    def create_payment(self, order_id, amount, order_info, redirect_url, ipn_url):
        request_id = str(uuid.uuid4())
        request_type = "captureWallet"
        extra_data = "" 
        amount_str = str(int(amount))
        
        # Tạo chuỗi raw signature theo chuẩn MoMo V2
        raw_signature = f"accessKey={self.access_key}&amount={amount_str}&extraData={extra_data}&ipnUrl={ipn_url}&orderId={order_id}&orderInfo={order_info}&partnerCode={self.partner_code}&redirectUrl={redirect_url}&requestId={request_id}&requestType={request_type}"
        
        # Ký chữ ký HMAC SHA256
        signature = hmac.new(self.secret_key.encode('utf-8'), raw_signature.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Dữ liệu gửi đi - Chỉ giữ lại các trường bắt buộc để tránh sai lệch chữ ký
        payload = {
            "partnerCode": self.partner_code,
            "requestId": request_id,
            "amount": int(amount),
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": redirect_url,
            "ipnUrl": ipn_url,
            "lang": "vi",
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature
        }
        
        try:
            # Sử dụng json=payload để requests tự động set Content-Type và encode chuẩn
            response = requests.post(self.endpoint, json=payload)
            return response.json()
        except Exception as e:
            return {"resultCode": -1, "message": str(e)}

    def validate_signature(self, response_data):
        # Kiểm tra chữ ký khi MoMo redirect về hoặc gọi IPN
        signature = response_data.get('signature')
        
        # Các tham số dùng để kiểm tra chữ ký phản hồi
        # Theo MoMo V2: accessKey, amount, extraData, message, orderId, orderInfo, partnerCode, requestId, responseTime, resultCode, transId
        params = {
            "accessKey": self.access_key,
            "amount": str(response_data.get('amount')),
            "extraData": response_data.get('extraData', ''),
            "message": response_data.get('message'),
            "orderId": response_data.get('orderId'),
            "orderInfo": response_data.get('orderInfo'),
            "partnerCode": response_data.get('partnerCode'),
            "requestId": response_data.get('requestId'),
            "responseTime": str(response_data.get('responseTime')),
            "resultCode": str(response_data.get('resultCode')),
            "requestType": response_data.get('requestType', 'captureWallet'), # Thường không có trong redirect nhưng có thể có trong IPN
            "transId": str(response_data.get('transId'))
        }
        
        # Chuỗi raw theo tài liệu MoMo (loại bỏ các trường None hoặc không cần thiết tùy phiên bản, nhưng chuẩn V2 là đầy đủ)
        raw_signature = f"accessKey={params['accessKey']}&amount={params['amount']}&extraData={params['extraData']}&message={params['message']}&orderId={params['orderId']}&orderInfo={params['orderInfo']}&partnerCode={params['partnerCode']}&requestId={params['requestId']}&responseTime={params['responseTime']}&resultCode={params['resultCode']}&transId={params['transId']}"
        
        calculated_signature = hmac.new(self.secret_key.encode('utf-8'), raw_signature.encode('utf-8'), hashlib.sha256).hexdigest()
        
        return signature == calculated_signature
