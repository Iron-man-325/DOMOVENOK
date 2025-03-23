from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    #  path('', views.index_page, name='index'),
     path('admin/', views.apartment_list_admin_page, name='apartment_list'),
     path('add/', views.add_apartment_page, name='main'),
     path('', views.apartment_list_page, name='main'),
     path('login/', views.login_view, name='login'),
    # path('registration/', views.registration_page, name='registration'),
    # path('login/', views.login_page, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
