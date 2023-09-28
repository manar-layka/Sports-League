import csv
import io

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import GameAddForm, GameEditForm
from .models import Game, Team


# Create your views here.

# CBV
from .strategy import DefaultPointsCalculation


class UploadCSVView(LoginRequiredMixin, View):
    template_name = 'sport_league_app/upload_csv.html'

    def get(self, request):
        teams = Team.objects.all().order_by('-points', 'name')
        ranking_data = []
        for rank, team in enumerate(teams, start=1):
            ranking_data.append({
                'rank': rank,
                'name': team.name,
                'points': team.points
            })
        return render(request, self.template_name, {'ranking': ranking_data})

    def post(self, request):
        if request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            file = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(file)
            next(io_string)
            try:
                for row in csv.reader(io_string, delimiter=','):
                    if len(row) != 4:
                        return JsonResponse({'error_message': 'Invalid CSV Format'})
                    first_team_name, first_team_score, second_team_name, second_team_score = row
                    first_team, first_team_created = Team.objects.get_or_create(name=first_team_name)
                    second_team, second_team_created = Team.objects.get_or_create(name=second_team_name)

                    game = Game.objects.create(
                        first_team=first_team,
                        first_team_score=first_team_score,
                        second_team=second_team,
                        second_team_score=second_team_score,
                    )

                teams = Team.objects.all().order_by('-points', 'name')
                ranking_data = []
                for rank, team in enumerate(teams, start=1):
                    ranking_data.append({
                        'rank': rank,
                        'name': team.name,
                        'points': team.points
                    })
                return render(request, self.template_name, {'ranking': ranking_data})

            except Exception as e:
                return render(request, self.template_name, {'error_message': str(e)})

        return render(request, self.template_name)


class GameList(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'sport_league_app/games_list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class GameAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Game
    form_class = GameAddForm
    template_name = 'sport_league_app/add_game.html'
    success_url = reverse_lazy('sports_league_app:upload_csv')

    def form_valid(self, form):
        game = form.save()
        messages.success(self.request, f'{game} Game Added successfully.', extra_tags='success-message')
        return super(GameAddView, self).form_valid(form)

    def form_invalid(self, form):
        super().form_invalid(form)

        return self.render_to_response({"errors": form.errors}, status=400)


class GameEditView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameEditForm
    template_name = 'sport_league_app/edit_game.html'
    success_url = reverse_lazy('sports_league_app:games_list')
    pk_url_kwarg = 'pk'

    def form_valid(self, form, points_strategy=None):
        if points_strategy is None:
            points_strategy = DefaultPointsCalculation()
        cleaned_data = form.cleaned_data
        game = self.get_object()
        points_strategy.update_teams(game, delete=True)
        game.first_team_score = cleaned_data['first_team_score']
        game.second_team_score = cleaned_data['second_team_score']
        game.save()
        points_strategy.update_teams(game)
        messages.success(self.request, 'Game Has Been Edited successfully.', extra_tags='success-message')
        return super().form_valid(form)


class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    template_name = 'sport_league_app/delete_game.html'
    success_url = reverse_lazy('sports_league_app:games_list')

    def delete(self, request, *args, **kwargs):
        game = self.get_object()
        messages.success(request, f'{game} has been deleted successfully.', extra_tags='success-message')
        return super(GameDeleteView, self).delete(request, *args, **kwargs)


# FBV

# def upload_csv(request):
#     if request.method == "POST" and request.FILES['csv_file']:
#         csv_file = request.FILES['csv_file']
#         file = csv_file.read().decode('UTF-8')
#         io_string = io.StringIO(file)
#         next(io_string)
#         try:
#             for row in csv.reader(io_string, delimiter=','):
#                 if len(row) != 4:
#                     return JsonResponse({'error_message': 'Invalid CSV Format'})
#                 first_team_name, first_team_score, second_team_name, second_team_score = row
#                 first_team, first_team_created = Team.objects.get_or_create(name=first_team_name)
#                 second_team, second_team_created = Team.objects.get_or_create(name=second_team_name)
#
#                 update_teams(first_team, first_team_score, second_team, second_team_score)
#
#             teams = Team.objects.all().order_by('-points', 'name')
#             ranking_data = []
#             for rank, team in enumerate(teams, start=1):
#                 ranking_data.append({
#                     'rank': rank,
#                     'name': team.name,
#                     'points': team.points
#                 })
#             return JsonResponse({'ranking': ranking_data})
#
#         except Exception as e:
#             return render(request, 'sport_league_app/upload_csv.html', {'error_message': str(e)})
#
#     return render(request, 'sport_league_app/upload_csv.html')

# def add_game(request):
#     if request.method == 'POST':
#         form = GameForm(request.POST)
#         if form.is_valid():
#             cleaned_data = form.cleaned_data
#             first_team_name = cleaned_data['first_team']
#             first_team_score = cleaned_data['first_team_score']
#             second_team_name = cleaned_data['second_team']
#             second_team_score = cleaned_data['second_team_score']
#             first_team, first_team_created = Team.objects.get_or_create(name=first_team_name)
#             second_team, second_team_created = Team.objects.get_or_create(name=second_team_name)
#             update_teams(first_team, first_team_score, second_team, second_team_score)
#             return redirect('sports_league_app:upload_csv', )
#     else:
#         form = GameForm()
#
#     return render(request, 'sport_league_app/add_game.html', {'form': form})

# def game_list(request):
#     games = Game.objects.all()
#     return render(request, 'sport_league_app/games_list.html', {'games': games})


# def edit_game(request, game_id):
#     game = get_object_or_404(Game, pk=game_id)
#
#     if request.method == 'POST':
#         first_team_score = request.POST.get('first_team_score')
#         second_team_score = request.POST.get('second_team_score')
#
#         if first_team_score is None or second_team_score is None:
#             return render(request, 'sport_league_app/edit_game.html',
#                           {'game': game, 'error_message': 'Please fill in all fields.'})
#
#         game.first_team_score = first_team_score
#         game.second_team_score = second_team_score
#         game.save()
#         return redirect('sports_league_app:games_list')
#
#     return render(request, 'sport_league_app/edit_game.html', {'game': game})


# def delete_game(request, game_id):
#     game = get_object_or_404(Game, pk=game_id)
#
#     if request.method == 'POST':
#         game.delete()
#         return redirect('sports_league_app:games_list')
#
#     return render(request, 'sport_league_app/delete_game.html', {'game': game})
