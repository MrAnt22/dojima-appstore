import sys
from django.apps import AppConfig
from django.db.utils import OperationalError

class MembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'members'
    
    def ready(self):
        # Avoid running during migrations or management commands
        if 'runserver' not in sys.argv:
            return
        
        from django.db.utils import OperationalError, ProgrammingError
        try:
            from members.models import Category
            for cat_name in ['App', 'Post']:
                Category.objects.get_or_create(name=cat_name)
        except (OperationalError, ProgrammingError):
            # DB or table not ready — skip setup
            pass
