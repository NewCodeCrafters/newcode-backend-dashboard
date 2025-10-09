from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'

    def ready(self):
        print("🔔 Notifications app is ready and signals loaded!")  
        import apps.notifications.signals
