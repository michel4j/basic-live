from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from basiclive.core.lims.models import Project


def get_current_project(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return None

    session = getattr(request, 'session', None)
    active_project_id = session.get('active_project_id') if session else None

    if active_project_id:
        if user.is_superuser:
            project = Project.objects.filter(id=active_project_id).first()
        else:
            project = user.get_projects().filter(id=active_project_id).first()
        if project:
            return project
        elif session and 'active_project_id' in session:
            del session['active_project_id']

    # Fallback to user.default_project if set
    if getattr(user, 'default_project_id', None):
        if user.is_superuser:
            project = user.default_project
        else:
            project = user.get_projects().filter(id=user.default_project_id).first()
        if project:
            if session is not None:
                session['active_project_id'] = project.id
            return project
        else:
            user.default_project = None
            user.save(update_fields=['default_project'])

    # If user has exactly one project, auto-select it
    user_projects = user.get_projects()
    if user_projects.count() == 1:
        project = user_projects.first()
        if session is not None:
            session['active_project_id'] = project.id
        user.default_project = project
        user.save(update_fields=['default_project'])
        return project

    return None


class ProjectContextMiddleware(MiddlewareMixin):
    """
    Middleware that sets `request.project` as a lazy object resolving the active
    project context from the user's session or default project.
    """
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            request.project = None
        else:
            request.project = SimpleLazyObject(lambda: get_current_project(request))
