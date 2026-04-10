from django.contrib import admin
from django.utils.html import format_html


class WorkflowAdmin(admin.ModelAdmin):
    """
    Base admin class for BaseWorkflow subclasses.

    Do not register this class directly. Use WorkflowViewSet, which builds a
    concrete subclass with the correct editor URL namespace baked in, then
    registers it automatically.

    Subclasses must implement get_editor_url(obj) → str.
    """

    @admin.display(description='Nodes')
    def _node_count(self, obj) -> int:
        return len((obj.workflow_contents or {}).get('nodes', []))

    @admin.display(description='Edges')
    def _edge_count(self, obj) -> int:
        return len((obj.workflow_contents or {}).get('edges', []))

    @admin.display(description='Diagram editor')
    def _editor_link(self, obj) -> str:
        if not obj.pk:
            return '(save the workflow first)'

        url = self.get_editor_url(obj)
        return format_html('<a class="button" href="{}">&#9998; Edit Diagram</a>', url)

    def get_editor_url(self, obj) -> str:
        """Return the editor URL for obj. Implemented by WorkflowViewSet."""
        raise NotImplementedError(
            f'{self.__class__.__name__} must implement get_editor_url()'
        )


class SimpleWorkflowAdmin(WorkflowAdmin):
    """
    Concrete admin for SimpleWorkflow.

    Registered by SimpleWorkflowViewSet, not directly. The editor_url_name
    class attribute is set by WorkflowViewSet.build_admin_class() to match
    whatever namespace the viewset was registered under.
    """

    # Injected by WorkflowViewSet.build_admin_class(), e.g.:
    #   'workflow_editor_django.example:editor'
    editor_url_name: str = ''

    list_display = ('title', '_node_count', '_edge_count', 'updated_at', '_editor_link')
    readonly_fields = ('created_at', 'updated_at', '_editor_link')
    fields = ('title', '_editor_link', 'created_at', 'updated_at')

    def get_editor_url(self, obj) -> str:
        from django.urls import reverse
        return reverse(self.editor_url_name, kwargs={'pk': obj.pk})
