from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from sports_league_app.strategy import DefaultPointsCalculation

# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=300, verbose_name=_("Team Name"), null=False, blank=False, unique=True)
    wins = models.IntegerField(default=0, null=True, blank=True)
    draws = models.IntegerField(default=0, null=True, blank=True)
    loses = models.IntegerField(default=0, null=True, blank=True)
    points = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    @cached_property
    def games_count(self):
        return self.first_team_results.all().count() + self.second_team_results.all().count()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, points_strategy=None):
        if points_strategy is None:
            points_strategy = DefaultPointsCalculation()

        self.points = points_strategy.calculate_points(self)
        super(Team, self).save()


class Game(models.Model):
    first_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="first_team_results")
    first_team_score = models.PositiveIntegerField()
    second_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="second_team_results")
    second_team_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_team} vs {self.second_team}"

    def is_draw(self) -> bool:
        return self.first_team_score == self.second_team_score

    def is_winner(self, team: Team) -> bool:
        return self.winner_team == team

    def is_loser(self, team: Team) -> bool:
        return self.loser_team == team

    @property
    def winner_team(self):
        if self.is_draw():
            return None
        if self.first_team_score > self.second_team_score:
            return self.first_team
        return self.second_team

    @property
    def loser_team(self):
        if self.is_draw():
            return None

        if self.first_team_score > self.second_team_score:
            return self.second_team

        return self.first_team

    def delete(self, *args, **kwargs):
        points_strategy = kwargs.pop("points_strategy", None)
        if points_strategy is None:
            points_strategy = DefaultPointsCalculation()
        points_strategy.update_teams(self, delete=True)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        created = not self.pk
        super(Game, self).save(*args, **kwargs)
        points_strategy = kwargs.pop("points_strategy", None)
        if points_strategy is None:
            points_strategy = DefaultPointsCalculation()
        if created:
            points_strategy.update_teams(self)
