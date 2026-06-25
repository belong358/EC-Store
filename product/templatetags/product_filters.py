import html
from django import template

register = template.Library()


@register.filter(name='unescape_html')
def unescape_html(value):
    """
    Decode HTML entities thành ký tự Unicode thực sự.
    Ví dụ: &ocirc; → ô, &reg; → ®, &trade; → ™, &amp; → &
    Dùng sau |striptags để hiển thị text thuần không bị lỗi entity.
    """
    if not value:
        return value
    return html.unescape(value)