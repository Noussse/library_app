from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/',views.user_logout,name='logout'),
    path('book/',views.use_api,name='book'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

