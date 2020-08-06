from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.create_new_listing, name="new"),
    path("watchlist", views.watchlist_page, name = "watchlist"),
    path("category/<str:type>", views.specific_category_list, name="category"),
    path("<int:listing_id>", views.listing_detail, name="detail"),
    path("<int:listing_id>/bid", views.listing_bid, name = "listing_bid"),
    path("<int:listing_id>/comment", views.listing_comment, name ="listing_comment"),
    path("<int:listing_id>/close", views.listing_close, name = "listing_close"),
    path("<int:listing_id>/add", views.modify_watchlist, name = "modify_watchlist")
]
