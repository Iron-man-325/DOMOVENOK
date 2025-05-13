from datetime import date
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),

    path('add/', views.add_apartment, name='add_flat'),
    path('support/', views.support, name='support'),
    path('questions/', views.faq_questions, name='faq'),
    path('my-support-requests/', views.my_support_requests, name='my_support_requests'),

    path('flat-list/', views.flat_list, name='apartment_list'),
    path('flat/<int:flat_id>/', views.show_flat, name='flat_detail'),
    path('my-flats/', views.my_flats, name='my_flats'),

    path('sup/', views.sup, name='sup'),
    path('profile/', views.profile_page, name='profile'),
    path('stat/<int:flat_id>', views.stat, name='stat'),
    path('redact/', views.redact_profile, name='redact'),
    path('send-support-message/', views.send_support_message, name='send_support_message'),

    path('prob/', views.my_problems, name='prob'),
    path('error/', views.error_page, name='error'),

    path('login/', views.login_page, name='login'),
    path('registration/', views.registration_page, name='registration'),
    path('logout/', views.logout_page, name='logout'),
    path('search/', views.search_apartments, name='search_apartments'),

    path('flat/<int:apartment_id>/update_status/', views.update_apartment_status, name='update_apartment_status'),
    path('rent/<int:flat_id>/<int:dates>/', views.rent_apartment, name='rent'),
    path('connect/<int:flat_id>', views.contact_owner, name='connect'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
