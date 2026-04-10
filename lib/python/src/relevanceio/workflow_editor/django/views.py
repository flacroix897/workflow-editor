import json
from typing import Type

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from relevanceio.workflow_editor import DiagramEditor

from .admin import WorkflowAdmin
from .models import BaseWorkflow, SimpleWorkflow


class WorkflowViewSet:
    """
    Registers editor + save views, and a matching ModelAdmin, for a
    BaseWorkflow subclass — all under a single, consistent URL namespace.

    Usage in urls.py:

        from relevanceio.workflow_editor.django.views import WorkflowViewSet
        from myapp.models import MyWorkflow
        from myapp.admin import MyWorkflowAdmin

        viewset = WorkflowViewSet(
            model=MyWorkflow,
            app_name='myapp',
            url_prefix='workflows',
            admin_class=MyWorkflowAdmin,   # optional, defaults to WorkflowAdmin
        )

        # In the urlconf that carries app_name='myapp':
        urlpatterns = [*viewset.urls]

    Parameters
    ----------
    model:
        A concrete subclass of BaseWorkflow.
    app_name:
        The namespace this viewset's URLs will be registered under.
        Must match the app_name of the including urlconf so that
        reverse(f'{app_name}:editor', ...) works correctly.
    url_prefix:
        Path prefix for the generated URL patterns (no leading/trailing slash).
        Defaults to 'workflows'.
    workflow_name_attr:
        Attribute on the model instance used as the display name in the editor
        template. Defaults to 'title'. Falls back to str(obj) if absent.
    admin_class:
        A WorkflowAdmin subclass to register. When None (default), a concrete
        subclass is generated automatically with editor_url_name pre-filled.
    """

    def __init__(
        self,
        *,
        model: Type[BaseWorkflow],
        app_name: str,
        url_prefix: str = 'workflows',
        workflow_name_attr: str = 'title',
        admin_class: Type[WorkflowAdmin] | None = None,
    ) -> None:
        self.model = model
        self.app_name = app_name
        self.url_prefix = url_prefix.strip('/')
        self.workflow_name_attr = workflow_name_attr

        self._register_admin(admin_class)

    # ── Admin registration ────────────────────────────────────────────────────

    def _build_admin_class(self) -> Type[WorkflowAdmin]:
        """
        Produce a WorkflowAdmin subclass with editor_url_name set to the
        correct namespaced URL for this viewset.
        """
        editor_url_name = f'{self.app_name}:editor'

        return type(
            f'{self.model.__name__}Admin',
            (WorkflowAdmin,),
            {
                'editor_url_name': editor_url_name,
                'list_display': (
                    self.workflow_name_attr,
                    '_node_count',
                    '_edge_count',
                    '_editor_link',
                ),
                'readonly_fields': ('_editor_link',),
                'fields': (self.workflow_name_attr, '_editor_link'),
                'get_editor_url': lambda self_admin, obj: reverse(
                    editor_url_name,
                    kwargs={'pk': obj.pk},
                ),
            },
        )

    def _register_admin(self, admin_class: Type[WorkflowAdmin] | None) -> None:
        concrete_admin_class = admin_class or self._build_admin_class()

        if not admin.site.is_registered(self.model):
            admin.site.register(self.model, concrete_admin_class)

    # ── URL helpers ───────────────────────────────────────────────────────────

    @property
    def editor_url_name(self) -> str:
        return f'{self.app_name}:editor'

    @property
    def save_url_name(self) -> str:
        return f'{self.app_name}:save'

    @property
    def urls(self) -> list:
        """URL patterns to splice into a urlconf that carries app_name=self.app_name."""
        return [
            path(
                f'{self.url_prefix}/<int:pk>/editor/',
                self._editor_view,
                name='editor',
            ),
            path(
                f'{self.url_prefix}/<int:pk>/save/',
                self._save_view,
                name='save',
            ),
        ]

    # ── Hooks for subclasses ──────────────────────────────────────────────────

    def get_workflow_name(self, obj: BaseWorkflow) -> str:
        return str(getattr(obj, self.workflow_name_attr, obj))

    def get_workflow_contents(self, obj: BaseWorkflow) -> dict:
        return obj.workflow_contents or {}

    def save_workflow_contents(self, obj: BaseWorkflow, diagram: dict) -> None:
        obj.workflow_contents = diagram
        obj.save(update_fields=['workflow_contents'])

    def build_editor(self) -> DiagramEditor:
        """Override to register custom node types."""
        editor = DiagramEditor()
        editor.register_builtin_nodes()
        return editor

    # ── Internal views ────────────────────────────────────────────────────────

    @property
    def _editor_view(self):
        viewset = self

        @staff_member_required
        @require_GET
        def editor_view(request: HttpRequest, pk: int):
            obj = get_object_or_404(viewset.model, pk=pk)

            editor = viewset.build_editor()
            diagram = viewset.get_workflow_contents(obj)

            if diagram.get('nodes'):
                editor.deserialize(diagram)

            editor_html: str = editor.render(width='100%', height='100%')
            post_url: str = reverse(viewset.save_url_name, kwargs={'pk': pk})

            return render(request, 'admin/workflow_editor.html', {
                'editor_html': editor_html,
                'post_url': post_url,
                'title': 'Workflow Editor',
                'has_permission': True,
                'opts': viewset.model._meta,
                'workflow': obj,
            })

        return editor_view

    @property
    def _save_view(self):
        viewset = self

        @staff_member_required
        @csrf_protect
        @require_POST
        def save_view(request: HttpRequest, pk: int):
            obj = get_object_or_404(viewset.model, pk=pk)

            try:
                diagram: dict = json.loads(request.body)
            except json.JSONDecodeError as exc:
                return JsonResponse({'error': f'Invalid JSON: {exc}'}, status=400)

            if (
                not isinstance(diagram.get('nodes'), list)
                or not isinstance(diagram.get('edges'), list)
            ):
                return JsonResponse(
                    {'error': "Payload must contain 'nodes' and 'edges' arrays."},
                    status=400,
                )

            viewset.save_workflow_contents(obj, diagram)

            return JsonResponse({
                'status': 'ok',
                'nodes': len(diagram['nodes']),
                'edges': len(diagram['edges']),
            })

        return save_view


class SimpleWorkflowViewSet(WorkflowViewSet):
    """
    Ready-to-use WorkflowViewSet wired to SimpleWorkflow.

    The app_name must match the namespace the including urlconf declares.
    The example project passes app_name='workflow_editor_django.example'.
    """

    def __init__(self, *, app_name: str) -> None:
        super().__init__(
            model=SimpleWorkflow,
            app_name=app_name,
            url_prefix='workflows',
            workflow_name_attr='title',
        )
