from django.contrib import admin
from .models import Team, Game
# Register your models here.


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass
