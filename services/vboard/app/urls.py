from django.urls import path
from django.contrib.auth import views
from django.views.decorators.csrf import csrf_exempt
from . import views as views_app


urlpatterns = [
    path('', views_app.fv_app_index),
    path('login', csrf_exempt(views.LoginView.as_view()), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('usreg', views_app.fv_usreg, name='usreg'),
    path('bid', views_app.fv_bid, name='bid'),
    path('bid/<str:rq_idb>', views_app.fv_bid_id, name='bid_read'),
    path('bid_add', views_app.fv_bid_add, name='bid_add'),
    path('bid_upd/<str:rq_idb>', views_app.fv_bid_edit, name='bid_upd'),
    path('bid_del/<str:rq_idb>', views_app.fv_bid_del, name='bid_del'),
    path('promo_active', views_app.fv_promo_active, name='promo_active'),
    path('station', views_app.fv_station, name='station'),
#    path('init', views_app.fv_init),
    path('<str:rparam>', views_app.fv_rparam),

]