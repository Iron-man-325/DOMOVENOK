from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index_page, name='index'),
    path('support/', views.support, name='index'),
    path('questions/', views.faq_questions, name='index'),

    path('flat-list/', views.flat_list, name='index'),
    path('flat/<int:flat_id>/', views.show_flat, name='flat_detail'),
    path('my-flats/', views.my_flats, name='send_support_message'),

    path('sup/', views.sup, name='index'),
    path('profile/', views.profile, name='index'),
    path('stat/', views.stat, name='index'),
    path('redac/', views.redac_profile, name='index'),
    path('send-support-message/', views.send_support_message, name='send_support_message'),

    path('prob/', views.my_problems, name='logout'),
    path('error/', views.error, name='logout'),
    path('login/', views.login_view, name='login'),

    path('registration/', views.registration_page, name='registration'),
    path('login/', views.login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
