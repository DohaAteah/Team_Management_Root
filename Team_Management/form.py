from django import forms
from Team_Management.models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields=['title']
