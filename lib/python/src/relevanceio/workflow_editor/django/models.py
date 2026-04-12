from django.db import models


class BaseWorkflow(models.Model):
    """
    Abstract base model for all workflow instances.

    Subclasses must define their own primary key and any additional fields
    they need (title, owner, etc.). The only field provided here is
    workflow_contents, which stores the serialized diagram produced by
    DiagramEditor.serialize().
    """

    # Serialized diagram: {"nodes": [...], "edges": [...], "nodeTypes": [...]}
    workflow_contents = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class SimpleWorkflow(BaseWorkflow):
    """
    Ready-to-use workflow model with a title and timestamps.

    Use this directly, or treat it as a reference implementation when
    building a custom workflow model on top of BaseWorkflow.
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title
