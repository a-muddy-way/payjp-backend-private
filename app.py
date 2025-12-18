from flask import Flask, request, jsonify
import sqlite3
import os

from werkzeug.exceptions import HTTPException

app = Flask(__name__)
DB_FILE = "books.db"

@app.errorhandler(Exception)
def handle_exception(e):
    with open("fatal_error.log", "w") as f:
        f.write(str(e) + "\n")
        import traceback
        traceback.print_exc(file=f)
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    if query:
        # Search by title or author containing the query string (partial match)
        books_data = conn.execute(
            'SELECT * FROM books WHERE title LIKE ? OR author LIKE ?',
            (f'%{query}%', f'%{query}%')
        ).fetchall()
    else:
        # Return all books if no query (or limit to a reasonable number)
        books_data = conn.execute('SELECT * FROM books LIMIT 50').fetchall()
    
    conn.close()
    
    results = [dict(row) for row in books_data]
    return jsonify({"results": results, "count": len(results)})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

import payjp

# Pay.jp setup (Use env var or fallback for local dev)
# NOTE: In production (Render), set PAYJP_SECRET_KEY in environment variables.
payjp.api_key = os.getenv('PAYJP_SECRET_KEY', 'sk_test_933bc71b8e01aa31e9232c14')

@app.route('/purchase', methods=['POST'])
def purchase_book():
    print("DEBUG: /purchase called")
    try:
        data = request.json
        print(f"DEBUG: payload: {data}")
        if not data or 'book_id' not in data:
            return jsonify({"error": "book_id is required"}), 400
            
        book_id = data['book_id']
        
        conn = get_db_connection()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        conn.close()
        
        if not book:
            print("DEBUG: Book not found")
            return jsonify({"error": "Book not found"}), 404
            
        price = book['price']
        print(f"DEBUG: Book: {book['title']}, Price: {price}")
        
        if not price:
             return jsonify({"error": "Price not set for this book"}), 400

        # Execute payment using Pay.jp
        # Default currency is JPY. Using a test card token 'tok_visa' for demo purposes.
        # In a real app, 'card' would come from the frontend tokenization.
        print("DEBUG: Creating Pay.jp charge...")
        charge = payjp.Charge.create(
            amount=price,
            currency='jpy',
            card='tok_visa',
            description=f"Payment for {book['title']}"
        )
        print(f"DEBUG: Charge created: {charge.id}")
        
        return jsonify({
            "status": "success",
            "message": f"Purchased {book['title']} for {price} JPY",
            "charge_id": charge.id
        })

    except Exception as e:
        with open("error.log", "w") as f:
            f.write(str(e) + "\n")
            import traceback
            traceback.print_exc(file=f)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
