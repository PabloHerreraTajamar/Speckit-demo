from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """
        Import signal handlers when Django starts.

        This method is called when the app is ready to use.
        We import signals here to ensure they are registered.
        """
        import accounts.signals  # noqa: F401
