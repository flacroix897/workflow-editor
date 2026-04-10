from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/workflow/', include('workflow_editor_django.example.urls')),
    path('admin/', admin.site.urls),
]
