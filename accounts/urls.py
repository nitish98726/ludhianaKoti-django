from django.urls import path , include
from . import views


urlpatterns = [
    path("register/" , views.register , name = 'register'),
    path('login/<int:login_param>/' , views.login , name = 'login'),
    path('logout/' , views.logout , name = 'logout'), 
    path('activate/<uidb64>/<token>/' , views.activate ,name = "activate"),
    path("dashboard/" , views.dashboard , name = 'dashboard'),

]