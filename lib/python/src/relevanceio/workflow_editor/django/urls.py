from django.contrib import admin
from django.urls import path
from workflow_editor.views import workflow_editor_view, workflow_save_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Workflow editor — lives under /admin/ so the admin chrome renders correctly.
    path("admin/workflow/editor/", workflow_editor_view, name="workflow-editor"),

    # Your save endpoint (must validate CSRF + require staff login independently).
    path("admin/workflow/save/", workflow_save_view, name="workflow-save"),
]
