import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database connection helper
def get_db_connection():
    conn = psycopg2.connect(
        os.environ.get('DATABASE_URL'),
        cursor_factory=RealDictCursor  # Returns dict instead of tuples
    )
    return conn

@app.route('/')
def taskpane():
    return send_from_directory(os.path.dirname(__file__), 'taskpane.html')

# Serve JS from same folder as app.py
@app.route('/taskpane.js')
def serve_js():
    return send_from_directory(os.path.dirname(__file__), 'taskpane.js')


@app.route('/icon-16.png')
@app.route('/icon-32.png')
@app.route('/icon-64.png')
@app.route('/icon-80.png')
@app.route('/icon-128.png')
@app.route('/favicon.ico')
def icons():
    return '', 204

@app.route('/save', methods=['POST'])
def save_text():
    try:
        data = request.json
        text = data.get('text', '')
        user_email = data.get('userEmail', 'anonymous')  # Pass from frontend
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            'INSERT INTO notes (user_email, note_text) VALUES (%s, %s) RETURNING id',
            (user_email, text)
        )
        note_id = cur.fetchone()['id']
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✓ Note {note_id} saved for {user_email}")
        return jsonify({'status': 'saved', 'id': note_id})
    
    except Exception as e:
        print(f"Error saving note: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/notes', methods=['GET'])
def get_notes():
    """Retrieve user's notes"""
    try:
        user_email = request.args.get('userEmail', 'anonymous')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            'SELECT * FROM notes WHERE user_email = %s ORDER BY created_at DESC',
            (user_email,)
        )
        notes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({'notes': notes})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Local development only
    app.run(host='localhost', port=3000, ssl_context=('cert.pem', 'key.pem'), debug=True)

