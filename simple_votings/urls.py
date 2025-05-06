from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('add/', views.add_apartment, name='add'),
    path('support/', views.support, name='data'),
    path('questions/', views.faq_questions, name='faq'),
    path('my-support-requests/', views.my_support_requests, name='my_support_requests'),

    path('flat-list/', views.flat_list, name='apartment_list'),
    path('flat/<int:flat_id>/', views.show_flat, name='flat_detail'),
    path('my-flats/', views.my_flats, name='my_flats'),

    path('sup/', views.sup, name='sup'),
    path('profile/', views.profile, name='profile'),
    path('stat/<int:flat_id>/', views.stat, name='stat'),
    path('redac/', views.redac_profile, name='redac'),
    path('send-support-message/', views.send_support_message, name='send_support_message'),

    path('prob/', views.my_problems, name='prob'),
    path('error/', views.error, name='error'),
    path('', views.login_view, name='login'),

    path('registration/', views.registration_page, name='registration'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('prob/', views.my_problems, name='logout'),
    path('error/', views.error, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
