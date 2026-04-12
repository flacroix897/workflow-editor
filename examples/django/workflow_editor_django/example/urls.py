from relevanceio.workflow_editor.django.views import SimpleWorkflowViewSet

app_name = 'workflow_editor_django.example'

_viewset = SimpleWorkflowViewSet(app_name=app_name)

# Flat list — the namespace is registered by the outer include() in the
# project urlconf, which reads app_name from this module directly.
urlpatterns = _viewset.urls
