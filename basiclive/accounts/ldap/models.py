from basiclive.auth.ldap.models import on_user_create, on_user_delete, is_directory_management_enabled

# Legacy aliases
on_project_create = on_user_create
on_project_delete = on_user_delete

__all__ = ['on_user_create', 'on_user_delete', 'on_project_create', 'on_project_delete', 'is_directory_management_enabled']
