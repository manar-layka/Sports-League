from abc import ABC, abstractmethod


class PointsCalculationStrategy(ABC):
    @abstractmethod
    def calculate_points(self, team):
        pass

    @abstractmethod
    def update_teams(self, game, delete=False):
        pass


class DefaultPointsCalculation(PointsCalculationStrategy):
    def calculate_points(self, team):
        return team.wins * 3 + team.draws * 1 + team.loses * 0

    def update_teams(self, game, delete=False):
        first_team = game.first_team
        second_team = game.second_team
        if delete:
            if game.is_draw():
                first_team.draws -= 1
                second_team.draws -= 1
            elif game.is_winner(first_team):
                first_team.wins -= 1
                second_team.loses -= 1
            else:
                first_team.loses -= 1
                second_team.wins -= 1
        else:
            if game.is_draw():
                first_team.draws += 1
                second_team.draws += 1
            elif game.is_winner(first_team):
                first_team.wins += 1
                second_team.loses += 1
            else:
                first_team.loses += 1
                second_team.wins += 1

        first_team.save()
        second_team.save()


class AlternativePointsCalculation(PointsCalculationStrategy):
    def calculate_points(self, team):
        """
           Implement an alternative points calculation method here
           Example: return team.wins * 2 + team.draws * 1 + team.loses * 0
        """
        pass

    def update_teams(self, game, delete=False):
        """
            Implement a way to calculate team wins, draws and loses and update teams depending on it
        """
        pass
