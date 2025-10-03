from django.apps import AppConfig as app_config


class AppConfig(app_config):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
