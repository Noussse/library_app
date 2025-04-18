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
    
    # Author books
    path('author/<int:author_id>/', views.author_books, name='author_books'),
    
    # Genre books
    path('genre/<int:genre_id>/', views.genre_books, name='genre_books'),
    
    # Search
    path('search/', views.search_books, name='search_books'),
    
    # Browse pages
    path('browse/', views.browse_books, name='browse_books'),
    path('authors/', views.browse_authors, name='browse_authors'),
    path('genres/', views.browse_genres, name='browse_genres'),
    path('books/', views.browse_books, name='browse_books'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

