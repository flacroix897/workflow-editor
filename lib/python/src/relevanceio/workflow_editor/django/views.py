import json
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST


@staff_member_required
@require_GET
def workflow_editor_view(request):
    """
    Render the Django admin workflow editor page.

    Expects the following GET params (or override with your own lookup logic):
      - Override `diagram`, `node_types`, and `post_url` below with
        however you load/resolve them (e.g. from a model, session, etc.)
    """

    # ── Replace these with your actual data sources ───────────────────────────

    # A serialized diagram dict, or an empty diagram.
    diagram: dict = {
        "nodes": [],
        "edges": [],
        "nodeTypes": [],
    }

    # List of custom node type definition dicts.
    # Each dict mirrors the SerializedNodeType object schema.
    node_types: list[dict] = [
        # Example:
        # {
        #     "nodeClass": "TaskNode",
        #     "baseClass": "RectangleNode",
        #     "name": "Task",
        #     "defaultOptions": {"label": "New Task", "backgroundColor": "#f0f8ff"},
        #     "schema": {
        #         "assignee": {"label": "Assignee", "type": "text", "default": ""},
        #         "done": {"label": "Done", "type": "boolean", "default": False},
        #         "priority": {
        #             "label": "Priority",
        #             "type": "choice",
        #             "default": "medium",
        #             "choices": {"low": "Low", "medium": "Medium", "high": "High"},
        #         },
        #     },
        #     "visibleProps": ["label", "backgroundColor"],
        # }
    ]

    # URL that receives POST requests whenever the diagram changes.
    post_url: str = "/admin/workflow/save/"  # replace with reverse("your-save-view")

    # ─────────────────────────────────────────────────────────────────────────

    return render(request, "admin/workflow_editor.html", {

        # Serialise to JSON strings so the template can embed them safely.
        "diagram_json": json.dumps(diagram),
        "node_types_json": json.dumps(node_types),
        "post_url": post_url,
        # Standard admin context extras (title shown in the breadcrumb bar).
        "title": "Workflow Editor",
        "has_permission": True,
    })


# ── Save view ─────────────────────────────────────────────────────────────────

@staff_member_required
@csrf_protect
@require_POST
def workflow_save_view(request):
    """
    Receive a serialized diagram from the editor and persist it.

    The request body is the JSON string produced by editor.serialize(), which
    has the shape:
        {
            "nodes":     [ ...SerializedNode ],
            "edges":     [ ...SerializedEdge ],
            "nodeTypes": [ ...SerializedNodeType ]   # included by default
        }

    Replace the body of this view with your own persistence logic —
    examples for three common patterns are shown below.
    """
    try:
        diagram: dict = json.loads(request.body)
    except json.JSONDecodeError as exc:
        return JsonResponse({"error": f"Invalid JSON: {exc}"}, status=400)

    # Basic shape validation — the editor always sends these two keys.
    if not isinstance(diagram.get("nodes"), list) or not isinstance(diagram.get("edges"), list):
        return JsonResponse({"error": "Payload must contain 'nodes' and 'edges' arrays."}, status=400)

    # ── Option A: store as a JSON field on a model ────────────────────────────
    # from myapp.models import Workflow
    # obj = Workflow.objects.get(pk=request.GET.get("id"))
    # obj.diagram = diagram          # JSONField stores the dict directly
    # obj.save(update_fields=["diagram"])

    # ── Option B: write to a file (quick prototyping) ─────────────────────────
    # import pathlib, json
    # pathlib.Path("/tmp/workflow.json").write_text(json.dumps(diagram, indent=2))

    # ── Option C: cache / session (ephemeral, single-user) ───────────────────
    # request.session["workflow_diagram"] = diagram

    # ── Replace the pass below once you've chosen a strategy ─────────────────
    pass

    return JsonResponse({"status": "ok", "nodes": len(diagram["nodes"]), "edges": len(diagram["edges"])})
