import os
import sys
import requests
import random
import time
import shutil
import django
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile

# Add the parent directory (project root) to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # BookStore directory
parent_dir = os.path.dirname(current_dir)  # Project root directory
sys.path.append(parent_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineBookStore.settings')
django.setup()

# Import models
from BookStore.models import Book, Author, Genre

# List of genres to fetch
GENRES = [
    'fiction', 'fantasy', 'science_fiction', 'mystery', 'romance', 
    'thriller', 'historical_fiction', 'biography', 'philosophy',
    'psychology', 'business', 'self_help', 'poetry'
]

# Open Library API base URLs
SUBJECT_API_BASE_URL = "https://openlibrary.org/subjects/"
COVERS_API_BASE_URL = "https://covers.openlibrary.org/b/"

def get_books_by_genre(genre, limit=5):
    """Fetch books from Open Library for a specific genre"""
    url = f"{SUBJECT_API_BASE_URL}{genre}.json?limit={limit}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get('works', [])
    else:
        print(f"Error fetching books for genre {genre}: {response.status_code}")
        return []

def get_cover_url(cover_id, size="M"):
    """Generate cover URL from cover ID"""
    if not cover_id:
        return None
    return f"{COVERS_API_BASE_URL}id/{cover_id}-{size}.jpg"

def download_cover_image(cover_url):
    """Download cover image from URL safely"""
    if not cover_url:
        return None
    
    try:
        response = requests.get(cover_url, stream=True)
        if response.status_code == 200:
            if 'image' not in response.headers.get('Content-Type', ''):
                print("Downloaded content is not an image.")
                return None

            img_temp = NamedTemporaryFile(delete=True)
            shutil.copyfileobj(response.raw, img_temp)
            img_temp.flush()
            return img_temp
        else:
            print(f"Failed to download cover image: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading cover image: {e}")
        return None

def delete_all_books():
    """Delete all books, authors, and genres from the database"""
    print("Deleting all existing books, authors, and genres...")
    Book.objects.all().delete()
    Author.objects.all().delete()
    Genre.objects.all().delete()
    print("Cleanup done.")

def import_books():
    """Main function to import books from Open Library"""
    books_added = 0
    
    # Delete existing records
    delete_all_books()

    for genre_name in GENRES:
        print(f"Fetching books for genre: {genre_name}")
        
        books = get_books_by_genre(genre_name, limit=5)
        display_name = genre_name.replace('_', ' ').title()
        genre, _ = Genre.objects.get_or_create(name=display_name)
        
        for book_data in books:
            title = book_data.get('title', '')
            key = book_data.get('key', '').replace('/works/', '')
            cover_id = book_data.get('cover_id')
            cover_url = get_cover_url(cover_id) if cover_id else None

            if Book.objects.filter(open_library_key=key).exists():
                print(f"Book '{title}' already exists, skipping.")
                continue

            book = Book(
                title=title,
                open_library_key=key,
                description=book_data.get('description', {}).get('value', '') if isinstance(book_data.get('description'), dict) else book_data.get('description', ''),
                published_year=random.randint(1950, 2023),
                cover_url=cover_url
            )

            if cover_url:
                img_temp = download_cover_image(cover_url)
                if img_temp:
                    filename = f"{key}.jpg"
                    img_temp.seek(0)
                    book.cover_image.save(filename, ContentFile(img_temp.read()), save=False)
                    img_temp.close()

            book.save()
            book.genres.add(genre)

            if 'authors' in book_data:
                for author_data in book_data['authors']:
                    author_name = author_data.get('name', '')
                    author, _ = Author.objects.get_or_create(name=author_name)
                    book.authors.add(author)

            books_added += 1
            print(f"Added book: {title}")
            time.sleep(0.5)

    return books_added

if __name__ == "__main__":
    total_books = import_books()
    print(f"\n✅ Imported {total_books} books successfully!")
