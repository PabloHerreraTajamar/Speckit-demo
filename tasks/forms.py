"""
Forms for task management.
"""

from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and updating tasks.

    Excludes owner field (set automatically in view).
    """

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "priority", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task title",
                    "maxlength": "200",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task description (optional)",
                    "rows": 4,
                    "maxlength": "2000",
                }
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
