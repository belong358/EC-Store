from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'

    def ready(self):
        import home.signals  # noqa: F401  – kích hoạt signals khi app khởi động
