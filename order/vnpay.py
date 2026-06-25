import hashlib
import hmac
import urllib.parse

class vnpay:
    request_data = {}
    response_data = {}

    def __init__(self):
        self.request_data = {}
        self.response_data = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        # 1. Sắp xếp các tham số theo thứ tự a-z (VNPay yêu cầu)
        inputData = sorted(self.request_data.items())
        
        # 2. Lọc bỏ các tham số rỗng và tạo chuỗi query string
        # urlencode sẽ tự động mã hóa các ký tự đặc biệt đúng chuẩn
        cleaned_data = {k: v for k, v in inputData if v is not None and str(v) != ""}
        query_string = urllib.parse.urlencode(cleaned_data)
        
        # 3. Tạo chữ ký bảo mật từ chuỗi query string
        hash_value = self.__hmacsha512(secret_key, query_string)
        
        # 4. Trả về URL hoàn chỉnh
        return vnpay_payment_url + "?" + query_string + "&vnp_SecureHash=" + hash_value

    def validate_response(self, secret_key):
        vnp_SecureHash = self.response_data.get('vnp_SecureHash')
        
        # 1. Lấy tất cả tham số vnp_ trừ tham số hash
        params = {k: v for k, v in self.response_data.items() if k.startswith('vnp_') and k not in ['vnp_SecureHash', 'vnp_SecureHashType']}
        
        # 2. Sắp xếp tham số theo alphabet
        inputData = sorted(params.items())
        
        # 3. Tạo chuỗi dữ liệu để băm. 
        # VNPay 2.1.0 yêu cầu các giá trị phải được URL Encode (quote_plus)
        hasData = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in inputData])
        
        hashValue = self.__hmacsha512(secret_key, hasData)
        
        if vnp_SecureHash and hashValue:
            return vnp_SecureHash.lower() == hashValue.lower()
        return False

    def __hmacsha512(self, key, data):
        byteKey = str.encode(key)
        byteData = str.encode(data)
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
