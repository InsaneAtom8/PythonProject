from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

def fetch_description(work_key):
    """Fetch the full description from the /works/WORK_ID.json endpoint"""
    try:
        work_url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(work_url)
        if response.status_code == 200:
            data = response.json()
            description = data.get("description")
            if isinstance(description, dict):
                return description.get("value", "No description available")
            elif isinstance(description, str):
                return description
    except Exception:
        pass
    return "No description available"

def fetch_books(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    books = []
    if response.status_code == 200:
        data = response.json()
        docs = data.get('docs', [])[:30]  # Fetch fewer for performance
        random.shuffle(docs)
        for doc in docs[:10]:
            work_key = doc.get("key")  # e.g. "/works/OL12345W"


            book = {
                'title': doc.get('title', 'No title'),
                'author': ', '.join(doc.get('author_name', ['Unknown'])),
                'year': doc.get('first_publish_year', 'N/A'),
                'cover': f"http://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg"
                         if doc.get('cover_i') else None,

                'rating': round(random.uniform(3.0, 5.0), 1)
            }
            books.append(book)
    return books


@app.route('/', methods=['GET', 'POST'])
def index():
    query = ''
    selected_genre = ''
    genres = ['Fiction', 'Romance', 'Mystery', 'Fantasy', 'Science', 'History', 'Horror']

    if request.method == 'POST':
        query = request.form.get('query', '')
        selected_genre = request.form.get('genre', '')
        search_term = query or selected_genre
        books = fetch_books(search_term)
    else:
        books = fetch_books('bestsellers fiction')

    return render_template('index.html', books=books, genres=genres,
                           selected_genre=selected_genre, query=query)

if __name__ == '__main__':
    app.run(debug=True)