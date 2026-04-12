"""
URL patterns for relevanceio.workflow_editor.django.

This module intentionally exports nothing. URL registration is handled by
WorkflowViewSet (or SimpleWorkflowViewSet) in the consuming project's urlconf.

Example:

    # myproject/urls.py
    from django.urls import include, path
    from relevanceio.workflow_editor.django.views import SimpleWorkflowViewSet

    _viewset = SimpleWorkflowViewSet(app_name='myapp')

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('admin/workflow/', include((_viewset.urls, 'myapp'))),
    ]
"""
