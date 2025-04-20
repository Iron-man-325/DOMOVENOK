from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),
    path('flat-add/', views.add_apartment, name='flat_add'),
    path('questions/', views.faq_questions, name='faq'),
    path('flat-list/', views.flat_list, name='flat_list'),
    path('sup/', views.sup, name='sup'),
    path('support/', views.support, name='support'),
    path('profile/', views.profile_page, name='profile'),
    path('stat/', views.stat, name='stat'),
    path('redact/', views.redact_profile, name='redact_profile'),
    path('send-support-message/', views.send_support_message, name='send_support_message'),
    path('my-flats/', views.my_flats, name='my_flats'),
    path('registration/', views.registration_page, name='registration'),
    path('login/', views.login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('prob/', views.my_problems, name='logout'),
    path('error/', views.error, name='logout'),
    # path('registration/', views.registration_page, name='registration'),
    # path('login/', views.login_page, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
