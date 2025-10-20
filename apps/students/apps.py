from django.apps import AppConfig

class StudentsConfig(AppConfig):
<<<<<<< HEAD
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'


    def ready(self):
        import apps.students.signals

    
=======
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.students"
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547
