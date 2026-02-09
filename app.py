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
    return send_from_directory('.', 'taskpane.html')

@app.route('/taskpane.js')
def static_files(filename):
    return send_from_directory('.', 'taskpane.js')

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
        data = request.json or {}
        text = data.get('text', '').strip()
        user_email = data.get('userEmail', 'anonymous')

        print(f"[SAVE] Received text: {text[:50]}...", flush=True)
        print(f"[SAVE] User email: {user_email}", flush=True)

        if not text:
            return jsonify({'status': 'error', 'message': 'Empty text'}), 400

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

        print(f"[SAVE] ✓ Note {note_id} saved successfully!", flush=True)
        return jsonify({'status': 'saved', 'id': note_id})
        
    except Exception as e:
        print(f"[SAVE] ❌ Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# def save_text():
#     try:
#         data = request.json
#         text = data.get('text', '')
#         user_email = data.get('userEmail', 'anonymous')  # Pass from frontend
        
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         cur.execute(
#             'INSERT INTO notes (user_email, note_text) VALUES (%s, %s) RETURNING id',
#             (user_email, text)
#         )
#         note_id = cur.fetchone()['id']
        
#         conn.commit()
#         cur.close()
#         conn.close()
        
#         print(f"✓ Note {note_id} saved for {user_email}")
#         return jsonify({'status': 'saved', 'id': note_id})
    
#     except Exception as e:
#         print(f"Error saving note: {str(e)}")
#         return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/view-notes')
@app.route('/view-notes')
def view_notes():
    """Bulletproof notes viewer"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Simple query - no aliases
        cur.execute('SELECT id, user_email, note_text, created_at FROM notes ORDER BY created_at DESC LIMIT 20')
        notes = cur.fetchall()
        
        print(f"DEBUG: Found {len(notes)} notes")  # Check Render logs
        
        cur.close()
        conn.close()
        
        if not notes:
            return "<h1>✅ No notes yet</h1><p>Save some notes first!</p>"
        
        # Build simple table
        html = f"<h1>✅ {len(notes)} Notes Found!</h1>"
        html += "<table border='1' cellpadding='10' style='border-collapse: collapse;'>"
        html += "<tr style='background: #0078d4; color: white;'><th>ID</th><th>User</th><th>Note Preview</th><th>Date</th></tr>"
        
        for note in notes:
            # Safe indexing: note[0]=id, note[1]=email, note[2]=text, note[3]=date
            note_id = note[0]
            user_email = note[1] or 'anonymous'
            note_preview = (str(note[2])[:80] + '...') if len(str(note[2])) > 80 else str(note[2])
            note_date = str(note[3])
            
            html += f"<tr>"
            html += f"<td><strong>{note_id}</strong></td>"
            html += f"<td>{user_email}</td>"
            html += f"<td>{note_preview}</td>"
            html += f"<td>{note_date}</td>"
            html += f"</tr>"
        
        html += "</table>"
        html += f"<p><a href='/'>← Back to Notes App</a> | "
        html += f"<a href='/test-db'>Test DB</a></p>"
        
        return html
        
    except Exception as e:
        print(f"view_notes ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc(flush=True)
        return f"<h1>Database Error Details</h1><pre>{str(e)}</pre>"

@app.route('/test-db')
def test_db():
    """Quick database status check"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM notes')
        count = cur.fetchone()[0]
        cur.execute('SELECT id, user_email FROM notes ORDER BY id DESC LIMIT 3')
        recent = cur.fetchall()
        cur.close()
        conn.close()
        
        html = f"<h1>✅ Database Status</h1>"
        html += f"<p><strong>{count}</strong> total notes</p>"
        html += "<h3>Recent notes:</h3><ul>"
        for note in recent:
            html += f"<li>ID {note[0]}: {note[1]}</li>"
        html += "</ul>"
        html += f"<p><a href='/view-notes'>Full Notes</a> | <a href='/'>Notes App</a></p>"
        
        return html
        
    except Exception as e:
        return f"<h1>❌ DB Connection Failed</h1><p>{str(e)}</p>"




# @app.route('/notes', methods=['GET'])
# def get_notes():
#     """Retrieve user's notes"""
#     try:
#         user_email = request.args.get('userEmail', 'anonymous')
        
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         cur.execute(
#             'SELECT * FROM notes WHERE user_email = %s ORDER BY created_at DESC',
#             (user_email,)
#         )
#         notes = cur.fetchall()
        
#         cur.close()
#         conn.close()
        
#         return jsonify({'notes': notes})
    
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Detect environment
    is_production = os.environ.get('ENVIRONMENT') == 'production'
    
    if is_production:
        # Production: Gunicorn will handle this
        # Run with: gunicorn -w 4 -b 0.0.0.0:8000 app:app
        print("Production mode: Use Gunicorn to run this app")
    else:
        # Local development: Use Flask's built-in server
        print("Starting local development server...")
        print("Server running at https://localhost:3000")
        app.run(
            host='localhost', 
            port=3000, 
            ssl_context=('cert.pem', 'key.pem'), 
            debug=True
        )
