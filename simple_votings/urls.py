from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    #  path('', views.index_page, name='index'),
     path('admin/', views.apartment_list, name='apartment_list'),
     path('',views.add_apartment, name='main')
    # path('registration/', views.registration_page, name='registration'),
    # path('login/', views.login_page, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
