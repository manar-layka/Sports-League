from django.urls import path
from . import views

app_name = "sports_league_app"
urlpatterns = [
    path('', views.UploadCSVView.as_view(), name='upload_csv'),
    path('games-list/', views.GameList.as_view(), name='games_list'),
    path('add-game/', views.GameAddView.as_view(), name='add_game'),
    path('edit-game/<int:pk>/', views.GameEditView.as_view(), name='edit_game'),
    path('delete-game/<int:pk>/', views.GameDeleteView.as_view(), name='delete_game'),
    # path('', views.upload_csv, name='upload_csv'),
    # path('games-list/', views.game_list, name='games_list'),
    # path('add-game/', views.add_game, name='add_game'),
    # path('edit-game/<int:game_id>/', views.edit_game, name='edit_game'),
    # path('delete-game/<int:game_id>/', views.delete_game, name='delete_game'),
]
