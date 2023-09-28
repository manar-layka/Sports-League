
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from sports_league_app.strategy import DefaultPointsCalculation
# Create your tests here.
from .models import Game, Team

User = get_user_model()


class GameTestCase(TestCase):
    def setUp(self):
        self.first_team = Team.objects.create(name="Team 1")
        self.second_team = Team.objects.create(name="Team 2")
        self.game = Game.objects.create(first_team=self.first_team, first_team_score=2, second_team=self.second_team,
                                        second_team_score=1)
        self.draw_game = Game.objects.create(first_team=self.first_team, first_team_score=2,
                                             second_team=self.second_team, second_team_score=2)

    def test_is_draw(self):
        self.assertTrue(self.draw_game.is_draw())
        self.assertFalse(self.game.is_draw())

    def test_is_winner(self):
        self.assertTrue(self.game.is_winner(self.first_team))
        self.assertFalse(self.game.is_winner(self.second_team))

    def test_is_loser(self):
        self.assertFalse(self.game.is_loser(self.first_team))
        self.assertTrue(self.game.is_loser(self.second_team))

    def test_points(self):
        self.assertEqual(self.first_team.points, 4)
        self.assertEqual(self.second_team.points, 1)

    def tearDown(self):
        self.first_team.delete()
        self.second_team.delete()
        self.game.delete()
        self.draw_game.delete()


class UpdateTeamsTestCase(TestCase):
    def setUp(self):
        self.default_strategy_instance = DefaultPointsCalculation()
        self.first_team = Team.objects.create(name="Team 1", wins=2, draws=1, loses=0, points=7)
        self.second_team = Team.objects.create(name="Team 2", wins=1, draws=2, loses=0, points=5)
        self.game = Game.objects.create(first_team=self.first_team, first_team_score=2, second_team=self.second_team,
                                        second_team_score=1)
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_login_user(self):
        # test protected url
        response = self.client.get(reverse('sports_league_app:upload_csv'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('sports_league_app:upload_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_form_valid_with_default_strategy(self):
        self.test_login_user()
        with patch('sports_league_app.views.DefaultPointsCalculation') as MockDefaultPointsCalculation:
            mock_strategy_instance = MockDefaultPointsCalculation.return_value
            form_data = {'first_team_score': 3, 'second_team_score': 1}
            response = self.client.post(reverse('sports_league_app:edit_game', kwargs={
                'pk': self.game.pk}), data=form_data)
            mock_strategy_instance.update_teams.assert_called_with(self.game)
            self.game.refresh_from_db()
            self.assertEqual(self.game.first_team_score, 3)
            self.assertEqual(self.game.second_team_score, 1)
            mock_strategy_instance.update_teams.assert_called_with(self.game)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('sports_league_app:games_list'))

    def test_update_teams(self):
        self.test_login_user()
        self.default_strategy_instance.update_teams(self.game, delete=False)
        self.first_team.refresh_from_db()
        self.second_team.refresh_from_db()
        self.assertEqual(self.first_team.wins, 4)
        self.assertEqual(self.first_team.draws, 1)
        self.assertEqual(self.first_team.loses, 0)
        self.assertEqual(self.first_team.points, 13)

        self.assertEqual(self.second_team.wins, 1)
        self.assertEqual(self.second_team.draws, 2)
        self.assertEqual(self.second_team.loses, 2)
        self.assertEqual(self.second_team.points, 5)
        self.default_strategy_instance.update_teams(self.game, delete=True)
        self.first_team.refresh_from_db()
        self.second_team.refresh_from_db()
        self.assertEqual(self.first_team.wins, 3)
        self.assertEqual(self.first_team.draws, 1)
        self.assertEqual(self.first_team.loses, 0)
        self.assertEqual(self.first_team.points, 10)

        self.assertEqual(self.second_team.wins, 1)
        self.assertEqual(self.second_team.draws, 2)
        self.assertEqual(self.second_team.loses, 1)
        self.assertEqual(self.second_team.points, 5)

    def tearDown(self):
        self.first_team.delete()
        self.second_team.delete()


class UploadCSVViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_upload_csv_view(self):
        self.client.get(reverse('sports_league_app:upload_csv'))
        csv_content = (
            "Team_1 name,Team_1 score,Team_2 name,Team_2 score\n"
            "First Team,3,Second Team,3\n"
        )
        csv_file = SimpleUploadedFile("test_file.csv", bytes(csv_content, encoding='utf-8'), content_type="text/csv")
        response = self.client.post(reverse('sports_league_app:upload_csv'), {'csv_file': csv_file})
        self.assertIn('ranking', response.context)
        self.assertEqual([{'rank': 1, 'name': 'First Team', 'points': 1},
                          {'rank': 2, 'name': 'Second Team', 'points': 1}],
                         response.context['ranking'])


class GameAddViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')
    def test_game_add_view(self):
        self.client.get(reverse('sports_league_app:add_game'))
        first_team = Team.objects.create(name='First Team')
        second_team = Team.objects.create(name='Second Team')

        data = {
            'first_team': first_team.name,
            'first_team_score': 3,
            'second_team': second_team.name,
            'second_team_score': 2,
        }
        response = self.client.post(reverse('sports_league_app:add_game'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sports_league_app:upload_csv'))
        first_team.refresh_from_db()
        second_team.refresh_from_db()
        self.assertEqual(first_team.wins, 1)
        self.assertEqual(second_team.loses, 1)

        # Testing with new teams, not added yet
        data = {
            'first_team': 'New First Team',
            'first_team_score': 3,
            'second_team': 'New Second Team',
            'second_team_score': 2,
        }
        response = self.client.post(reverse('sports_league_app:add_game'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sports_league_app:upload_csv'))
        self.assertTrue(Team.objects.filter(name='New First Team').exists())
        self.assertTrue(Team.objects.filter(name='New Second Team').exists())
        new_first_team = Team.objects.get(name='New First Team')
        new_second_team = Team.objects.get(name='New Second Team')
        new_first_team.refresh_from_db()
        new_second_team.refresh_from_db()
        self.assertEqual(first_team.wins, 1)
        self.assertEqual(second_team.loses, 1)


class GameEditViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_game_edit_view(self):
        first_team = Team.objects.create(name='Team 1')
        second_team = Team.objects.create(name='Team 2')
        game = Game.objects.create(first_team=first_team, first_team_score=2, second_team=second_team,
                                   second_team_score=1)
        first_team.refresh_from_db()
        second_team.refresh_from_db()
        self.assertEqual(first_team.wins, 1)
        self.assertEqual(second_team.loses, 1)

        self.client.get(reverse('sports_league_app:edit_game', args=(game.pk,)))

        data = {
            first_team: first_team.pk,
            second_team: second_team.pk,
            'first_team_score': 2,
            'second_team_score': 3,
        }

        response = self.client.post(reverse('sports_league_app:edit_game', args=[game.id]), data)
        self.assertRedirects(response, reverse('sports_league_app:games_list'))
        first_team.refresh_from_db()
        second_team.refresh_from_db()
        self.assertEqual(first_team.wins, 0)
        self.assertEqual(first_team.loses, 1)
        self.assertEqual(first_team.points, 0)
        self.assertEqual(second_team.loses, 0)
        self.assertEqual(second_team.wins, 1)
        self.assertEqual(second_team.points, 3)
