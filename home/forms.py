from django import forms


# Lớp SearchForm dùng để tạo form tìm kiếm với 1 trường:
# - query: trường văn bản để nhập từ khóa tìm kiếm (tối đa 100 ký tự)
# Tìm kiếm trên toàn bộ sản phẩm, không lọc theo danh mục.

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)  # Trường nhập văn bản tìm kiếm
