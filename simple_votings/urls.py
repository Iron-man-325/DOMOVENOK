from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
     path('', views.index_page, name='index'),
     path('flat-list/', views.flat_list, name='index'),
     path('sup/', views.sup, name='index'),
     path('profile/', views.profile, name='index'),
     path('stat/', views.stat, name='index'),
     path('redac/', views.redac_profile, name='index'),
     path('send-support-message/', views.send_support_message, name='send_support_message'),
     path('my-flats/', views.my_flats, name='send_support_message'),
    # path('registration/', views.registration_page, name='registration'),
    # path('login/', views.login_page, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
