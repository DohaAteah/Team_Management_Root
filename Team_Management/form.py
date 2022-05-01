from django import forms
from Team_Management.models import Team,Task

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields=['title']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields=['title']