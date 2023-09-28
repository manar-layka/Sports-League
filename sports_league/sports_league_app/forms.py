from django import forms

from .models import Game, Team


class GameAddForm(forms.ModelForm):
    first_team = forms.CharField(max_length=300)
    second_team = forms.CharField(max_length=300)

    def clean_first_team(self):
        first_team = self.cleaned_data["first_team"]
        team, created = Team.objects.get_or_create(name=first_team)
        return team

    def clean_second_team(self):
        second_team = self.cleaned_data["second_team"]
        team, created = Team.objects.get_or_create(name=second_team)
        return team

    class Meta:
        model = Game
        fields = ["first_team", "first_team_score", "second_team", "second_team_score"]


class GameEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameEditForm, self).__init__(*args, **kwargs)
        self.fields["first_team"].disabled = True
        self.fields["second_team"].disabled = True

    class Meta:
        model = Game
        fields = ["first_team", "second_team", "first_team_score", "second_team_score"]
