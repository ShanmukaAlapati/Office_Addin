import os
import psycopg2
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


# ---------- DB CONNECTION ----------

def get_db_connection():
    """
    Connect to Render PostgreSQL (or whatever DATABASE_URL points to).
    Uses a normal cursor for simplicity.
    """
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn


# ---------- UI ROUTES (HTML + JS) ----------

@app.route("/")
def taskpane():
    # Serve taskpane.html from the same directory as app.py
    return send_from_directory(os.path.dirname(__file__), "taskpane.html")


@app.route("/taskpane.js")
def serve_js():
    # Serve taskpane.js from the same directory as app.py
    return send_from_directory(os.path.dirname(__file__), "taskpane.js")


# Outlook icon routes (can be empty 204s for now)
@app.route("/icon-16.png")
@app.route("/icon-32.png")
@app.route("/icon-64.png")
@app.route("/icon-80.png")
@app.route("/icon-128.png")
@app.route("/favicon.ico")
def icons():
    return "", 204


# ---------- API: SAVE NOTE ----------

@app.route("/save", methods=["POST"])
def save_text():
    try:
        data = request.get_json() or {}
        text = (data.get("text") or "").strip()
        user_email = data.get("userEmail") or "anonymous"

        if not text:
            return jsonify({"status": "error", "message": "Empty text"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO notes (user_email, note_text) VALUES (%s, %s) RETURNING id",
            (user_email, text),
        )
        note_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        print(f"[SAVE] Note {note_id} saved for {user_email}", flush=True)
        return jsonify({"status": "saved", "id": note_id})

    except Exception as e:
        print(f"[SAVE] ERROR: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------- DEBUG: DB STATUS ----------

@app.route("/test-db")
def test_db():
    """Quick DB health check."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM notes")
        count = cur.fetchone()[0]

        cur.execute(
            "SELECT id, user_email FROM notes ORDER BY id DESC LIMIT 3"
        )
        recent = cur.fetchall()

        cur.close()
        conn.close()

        html = "<h1>✅ Database Connected</h1>"
        html += f"<p><strong>{count}</strong> total notes</p>"
        html += "<h3>Recent notes:</h3><ul>"
        for row in recent:
            html += f"<li>ID {row[0]}: {row[1]}</li>"
        html += "</ul>"
        html += "<p><a href='/view-notes'>View all notes</a> | <a href='/'>Notes app</a></p>"
        return html

    except Exception as e:
        print(f"[TEST-DB] ERROR: {e}", flush=True)
        return f"<h1>❌ DB Error</h1><p>{e}</p>"


# ---------- VIEW NOTES (HTML TABLE) ----------

@app.route("/view-notes")
def view_notes():
    """Simple HTML viewer for saved notes."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, user_email, note_text, created_at "
            "FROM notes ORDER BY created_at DESC LIMIT 50"
        )
        notes = cur.fetchall()

        cur.close()
        conn.close()

        html = f"<h1>{len(notes)} Notes Found</h1>"

        if not notes:
            html += "<p>No notes yet. Save some first!</p>"
            html += "<p><a href='/'>Notes app</a></p>"
            return html

        html += """
        <table border="1" cellspacing="0" cellpadding="8"
               style="border-collapse: collapse; width: 100%; font-family: Arial;">
          <tr style="background:#0078d4;color:white;">
            <th>ID</th>
            <th>User</th>
            <th>Note (preview)</th>
            <th>Created At</th>
          </tr>
        """

        for row in notes:
            note_id = row[0]
            user_email = row[1] or "anonymous"
            note_text = str(row[2]) if row[2] is not None else ""
            created_at = row[3]

            preview = note_text[:80] + "..." if len(note_text) > 80 else note_text

            html += (
                "<tr>"
                f"<td>{note_id}</td>"
                f"<td>{user_email}</td>"
                f"<td>{preview}</td>"
                f"<td>{created_at}</td>"
                "</tr>"
            )

        html += "</table>"
        html += "<p><a href='/'>Notes app</a> | <a href='/test-db'>Test DB</a></p>"

        return html

    except Exception as e:
        print(f"[VIEW-NOTES] ERROR: {e}", flush=True)
        return f"<h1>Database Error</h1><p>{e}</p>"


# ---------- LOCAL DEV ENTRYPOINT ----------

if __name__ == "__main__":
    # Local dev: uses your cert.pem/key.pem, port 3000
    app.run(
        host="localhost",
        port=3000,
        ssl_context=("cert.pem", "key.pem"),
        debug=True,
    )





























# import os
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from flask import Flask, request, jsonify, render_template, send_from_directory
# from flask_cors import CORS
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# # Database connection helper
# def get_db_connection():
#     conn = psycopg2.connect(
#         os.environ.get('DATABASE_URL'),
#         cursor_factory=RealDictCursor  # Returns dict instead of tuples
#     )
#     return conn

# @app.route('/')
# def taskpane():
#     return send_from_directory('.', 'taskpane.html')

# @app.route('/taskpane.js')
# def static_files():
#     return send_from_directory('.', 'taskpane.js')

# @app.route('/icon-16.png')
# @app.route('/icon-32.png')
# @app.route('/icon-64.png')
# @app.route('/icon-80.png')
# @app.route('/icon-128.png')
# @app.route('/favicon.ico')
# def icons():
#     return '', 204

# @app.route('/save', methods=['POST'])
# def save_text():
#     try:
#         data = request.json or {}
#         text = data.get('text', '').strip()
#         user_email = data.get('userEmail', 'anonymous')

#         print(f"[SAVE] Received text: {text[:50]}...", flush=True)
#         print(f"[SAVE] User email: {user_email}", flush=True)

#         if not text:
#             return jsonify({'status': 'error', 'message': 'Empty text'}), 400

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

#         print(f"[SAVE] ✓ Note {note_id} saved successfully!", flush=True)
#         return jsonify({'status': 'saved', 'id': note_id})
        
#     except Exception as e:
#         print(f"[SAVE] ❌ Error: {e}", flush=True)
#         import traceback
#         traceback.print_exc()
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# # def save_text():
# #     try:
# #         data = request.json
# #         text = data.get('text', '')
# #         user_email = data.get('userEmail', 'anonymous')  # Pass from frontend
        
# #         conn = get_db_connection()
# #         cur = conn.cursor()
        
# #         cur.execute(
# #             'INSERT INTO notes (user_email, note_text) VALUES (%s, %s) RETURNING id',
# #             (user_email, text)
# #         )
# #         note_id = cur.fetchone()['id']
        
# #         conn.commit()
# #         cur.close()
# #         conn.close()
        
# #         print(f"✓ Note {note_id} saved for {user_email}")
# #         return jsonify({'status': 'saved', 'id': note_id})
    
# #     except Exception as e:
# #         print(f"Error saving note: {str(e)}")
# #         return jsonify({'status': 'error', 'message': str(e)}), 500



# @app.route('/view-notes')
# @app.route('/view-notes')
# def view_notes():
#     """Bulletproof notes viewer - Python 3.11 compatible"""
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         cur.execute('SELECT id, user_email, note_text, created_at FROM notes ORDER BY created_at DESC LIMIT 20')
#         notes = cur.fetchall()
        
#         print(f"DEBUG: Found {len(notes)} notes")  # Safe print
        
#         cur.close()
#         conn.close()
        
#         if not notes:
#             return "<h1>✅ No notes yet</h1><p>Save some notes first!</p><hr><a href='/'>← Notes App</a>"
        
#         # Simple HTML table
#         html = f"<h1>✅ {len(notes)} Notes Found!</h1>"
#         html += "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; font-family: Arial;'>"
#         html += "<tr style='background: #0078d4; color: white;'><th>ID</th><th>User</th><th>Note Preview</th><th>Date</th></tr>"
        
#         for note in notes:
#             note_id = note[0]
#             user_email = note[1] or 'anonymous'
#             note_preview = (str(note[2])[:80] + '...') if len(str(note[2])) > 80 else str(note[2])
#             note_date = str(note[3])
            
#             html += f"<tr>"
#             html += f"<td><strong>{note_id}</strong></td>"
#             html += f"<td>{user_email}</td>"
#             html += f"<td>{note_preview}</td>"
#             html += f"<td>{note_date}</td>"
#             html += f"</tr>"
        
#         html += "</table>"
#         html += f"<hr><a href='/'>← Back to Notes App</a> | <a href='/test-db'>Test DB</a>"
        
#         return html
        
#     except Exception as e:
#         error_msg = f"view_notes ERROR: {str(e)}"
#         print(error_msg)  # Safe print
        
#         # Safe traceback (no flush)
#         import traceback
#         traceback.print_exc()  # Remove flush=True
        
#         return f"""
#         <h1>Database Error</h1>
#         <p><strong>{str(e)}</strong></p>
#         <hr>
#         <a href='/test-db'>Test Database</a> | 
#         <a href='/'>Notes App</a>
#         """

# @app.route('/test-db')
# def test_db():
#     """Quick database status check"""
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute('SELECT COUNT(*) FROM notes')
#         count = cur.fetchone()[0]
#         cur.execute('SELECT id, user_email FROM notes ORDER BY id DESC LIMIT 3')
#         recent = cur.fetchall()
#         cur.close()
#         conn.close()
        
#         html = f"<h1>✅ Database Status</h1>"
#         html += f"<p><strong>{count}</strong> total notes</p>"
#         html += "<h3>Recent notes:</h3><ul>"
#         for note in recent:
#             html += f"<li>ID {note[0]}: {note[1]}</li>"
#         html += "</ul>"
#         html += f"<p><a href='/view-notes'>Full Notes</a> | <a href='/'>Notes App</a></p>"
        
#         return html
        
#     except Exception as e:
#         return f"<h1>❌ DB Connection Failed</h1><p>{str(e)}</p>"




# # @app.route('/notes', methods=['GET'])
# # def get_notes():
# #     """Retrieve user's notes"""
# #     try:
# #         user_email = request.args.get('userEmail', 'anonymous')
        
# #         conn = get_db_connection()
# #         cur = conn.cursor()
        
# #         cur.execute(
# #             'SELECT * FROM notes WHERE user_email = %s ORDER BY created_at DESC',
# #             (user_email,)
# #         )
# #         notes = cur.fetchall()
        
# #         cur.close()
# #         conn.close()
        
# #         return jsonify({'notes': notes})
    
# #     except Exception as e:
# #         return jsonify({'status': 'error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     # Detect environment
#     is_production = os.environ.get('ENVIRONMENT') == 'production'
    
#     if is_production:
#         # Production: Gunicorn will handle this
#         # Run with: gunicorn -w 4 -b 0.0.0.0:8000 app:app
#         print("Production mode: Use Gunicorn to run this app")
#     else:
#         # Local development: Use Flask's built-in server
#         print("Starting local development server...")
#         print("Server running at https://localhost:3000")
#         app.run(
#             host='localhost', 
#             port=3000, 
#             ssl_context=('cert.pem', 'key.pem'), 
#             debug=True
#         )
