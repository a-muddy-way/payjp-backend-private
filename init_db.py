import sqlite3
import os

DB_FILE = "books.db"

def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price INTEGER,
            description TEXT
        )
    ''')
    
    # Load data from CSV
    import csv
    books = []
    
    # Render等の環境で、カレントディレクトリが異なる可能性を考慮して絶対パスまたは適切なパス解決を行うのが望ましいが、
    # ここではシンプルに同階層のファイルを読み込む
    csv_path = os.path.join(os.path.dirname(__file__), 'books.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            books.append((
                row['title'],
                row['author'],
                int(row['price']),
                row['description']
            ))

    cursor.executemany('''
        INSERT INTO books (title, author, price, description)
        VALUES (?, ?, ?, ?)
    ''', books)
    
    conn.commit()
    conn.close()
    print(f"Database initialized with {len(books)} dummy books.")

if __name__ == "__main__":
    init_db()
