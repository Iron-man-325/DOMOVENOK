from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    #  path('', views.index_page, name='index'),
     path('admin/', views.apartment_list, name='apartment_list'),
     path('',views.add_apartment, name='main'),
     path('login/', views.login_view, name='login'),
     path('flat/<int:flat_id>/', views.show_flat, name='flat_detail'),
     path('photo', views.add_image_page),
         # path('registration/', views.registration_page, name='registration'),
    # path('login/', views.login_page, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
