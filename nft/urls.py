from django.urls import path

from . import views
from .views import activate_account

urlpatterns = [
    path("", views.index, name="index"),
    path("success", views.success, name="success"),
    path("error", views.error, name="error"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_nft", views.create_nft, name="create_nft"),
    path("all_nfts", views.all_nfts, name="all_nfts"),
    path("close_auction/<int:auc_id>/", views.close, name="close"),
    path("delete_auction/<int:auc_id>/", views.delete_auction, name="delete_auction"),
    path("all_nfts/<int:auc_id>/", views.item_details, name="item_details"),
    path('activate/<slug:uidb64>/<slug:token>/', activate_account, name='activate')
]
