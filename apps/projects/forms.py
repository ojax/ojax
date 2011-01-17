from django import forms
from django.conf import settings

from projects.models import Project



class NewProjectForm(forms.ModelForm):
    # tags = forms.CharField(max_length=255, help_text="Press enter after each tag to add it")
    
    class Meta:
        model = Project
        exclude = ("created",)
