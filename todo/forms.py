from django import forms
from .models import Task

class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    # Add custom form fields or override field attributes as needed
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(completed=True)

    mark_completed.short_description = "Mark selected tasks as completed"