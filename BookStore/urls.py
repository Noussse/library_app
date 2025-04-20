from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),


    path('', views.home, name='home'),
    
    # Book detail
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Browse pages
    path('browse/', views.browse_books, name='browse_books'),
    path('books/', views.browse_books, name='browse_books'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

