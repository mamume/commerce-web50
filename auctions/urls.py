from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', views.create_listing, name="create_listing"),
    path('listing/<title>/<str:message>', views.listing, name='listing'),
    path('listing/<title>', views.listing, name='listing'),
    path('place_bid/<title>', views.place_bid, name="place_bid"),
    path('watchlist/<title>', views.watchlist, name='watchlist'),
    path('close_auction/<auction_id>', views.close_auction, name='close_auction'),
    path('add_comment/<auction_id>/<username>',
         views.add_comment, name='add_comment'),
    path('watchlist_page', views.watchlist_page, name='watchlist_page'),
    path("categories_list", views.categories_list, name='categories_list'),
    path('category_page/<category_id>',
         views.category_page, name='category_page')
]
