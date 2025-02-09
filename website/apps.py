from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'website'

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()