import os
import sys
import requests
import random
import time
import shutil
import django
import math
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
WORKS_API_BASE_URL = "https://openlibrary.org"

# Target approximately 100 books total
TOTAL_BOOKS_TARGET = 100
BOOKS_PER_GENRE = math.ceil(TOTAL_BOOKS_TARGET / len(GENRES))  # Evenly distribute across genres

def get_books_by_genre(genre, limit=10):
    """Fetch books from Open Library for a specific genre"""
    url = f"{SUBJECT_API_BASE_URL}{genre}.json?limit={limit}"
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json().get('works', [])
        else:
            print(f"Error fetching books for genre {genre}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception when fetching genre {genre}: {e}")
        return []

def get_book_details(work_key):
    """Fetch detailed information for a single book by its Open Library work key"""
    url = f"{WORKS_API_BASE_URL}{work_key}.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching book details for {work_key}: {response.status_code}")
    except Exception as e:
        print(f"Exception when fetching book details: {e}")
    return None

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

def get_description(book_data):
    """Extract the description of a book, handling various formats."""
    description = book_data.get('description', '')
    
    # If description is missing, return empty string
    if not description:
        return ''
    
    # If description is a dictionary, try to get 'value' field
    if isinstance(description, dict):
        return description.get('value', '')
    
    # If description is a string, return it directly
    if isinstance(description, str):
        return description
    
    # For any other type, convert to string and return
    return str(description)

def import_books():
    """Main function to import books from Open Library, limited to ~100 total"""
    books_added = 0
    books_skipped = 0
    books_failed = 0
    
    # Delete existing records
    delete_all_books()

    # Track books by key to avoid duplicates across genres
    processed_keys = set()
    
    # Process each genre
    for genre_name in GENRES:
        print(f"\nFetching books for genre: {genre_name}")
        
        # Get books per genre based on target total
        books_to_fetch = BOOKS_PER_GENRE
        
        books = get_books_by_genre(genre_name, limit=books_to_fetch + 5)  # Get a few extra to account for potential skips
        print(f"Found {len(books)} books in genre {genre_name}")
        
        display_name = genre_name.replace('_', ' ').title()
        genre, _ = Genre.objects.get_or_create(name=display_name)
        
        genre_books_added = 0
        
        for book_data in books:
            # Check if we've reached our target for this genre
            if genre_books_added >= books_to_fetch:
                print(f"Reached target of {books_to_fetch} books for genre {genre_name}")
                break
                
            # Check if we've reached our total target
            if books_added >= TOTAL_BOOKS_TARGET:
                print(f"Reached total target of {TOTAL_BOOKS_TARGET} books")
                break
                
            try:
                title = book_data.get('title', '')
                if not title:
                    print("Skipping book with no title")
                    books_skipped += 1
                    continue
                    
                key = book_data.get('key', '').replace('/works/', '')
                if not key:
                    print(f"Skipping book '{title}' with no key")
                    books_skipped += 1
                    continue
                
                # Skip if we've already processed this book (across genres)
                if key in processed_keys:
                    print(f"Already processed book '{title}' in another genre, skipping.")
                    books_skipped += 1
                    continue
                    
                print(f"\nProcessing book: {title} (Key: {key})")
                
                # Check if book already exists
                if Book.objects.filter(open_library_key=key).exists():
                    print(f"Book '{title}' already exists, skipping.")
                    books_skipped += 1
                    continue
                
                # Fetch detailed book information
                detailed_data = get_book_details(book_data.get('key'))
                
                # Get description from detailed data if available, otherwise from original data
                if detailed_data and ('description' in detailed_data):
                    description = get_description(detailed_data)
                    print(f"Using description from detailed data: {description[:50]}..." if description else "No description found in detailed data")
                else:
                    description = get_description(book_data)
                    print(f"Using description from basic data: {description[:50]}..." if description else "No description found in basic data")
                
                # Get cover image
                cover_id = book_data.get('cover_id')
                cover_url = get_cover_url(cover_id) if cover_id else None
                print(f"Cover URL: {cover_url}")
                
                # Create new book
                book = Book(
                    title=title,
                    open_library_key=key,
                    description=description,
                    published_year=random.randint(1950, 2023),
                    cover_url=cover_url
                )

                # Download and save cover image
                if cover_url:
                    img_temp = download_cover_image(cover_url)
                    if img_temp:
                        filename = f"{key}.jpg"
                        img_temp.seek(0)
                        book.cover_image.save(filename, ContentFile(img_temp.read()), save=False)
                        img_temp.close()
                        print("Cover image saved successfully")
                    else:
                        print("Failed to download cover image")

                book.save()
                book.genres.add(genre)
                
                # Process authors
                if 'authors' in book_data:
                    for author_data in book_data['authors']:
                        author_name = author_data.get('name', '')
                        if author_name:
                            author, _ = Author.objects.get_or_create(name=author_name)
                            book.authors.add(author)
                            print(f"Added author: {author_name}")

                # Mark as processed
                processed_keys.add(key)
                books_added += 1
                genre_books_added += 1
                print(f"✅ Added book: {title}")
                
                # Add a small delay to avoid overloading the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing book: {e}")
                books_failed += 1
                continue

    return books_added, books_skipped, books_failed

if __name__ == "__main__":
    print(f"Starting book import process (Target: ~{TOTAL_BOOKS_TARGET} books total)...")
    print(f"Will import approximately {BOOKS_PER_GENRE} books per genre")
    
    total_books, skipped_books, failed_books = import_books()
    
    print(f"\n✅ Import summary:")
    print(f"- Successfully imported: {total_books} books")
    print(f"- Skipped: {skipped_books} books")
    print(f"- Failed: {failed_books} books")