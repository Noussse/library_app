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

    path('book/<int:book_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('book/<int:book_id>/favorite/', views.favorite_book, name='favorite_book'),
    path('book/<int:book_id>/toggle-reading-list/', views.toggle_reading_list, name='toggle_reading_list'),
    path('book/<int:book_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-books/', views.my_books, name='my_books'),
    path('book/<int:book_id>/remove-favorite/', views.remove_favorite, name='remove_favorite'),
    path('book/<int:book_id>/remove-reading/', views.remove_reading, name='remove_reading'),
    


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
