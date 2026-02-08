import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_database():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = conn.cursor()
    
    # Create notes table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255),
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            email_subject VARCHAR(500),
            email_sender VARCHAR(255)
        );
        
        CREATE INDEX IF NOT EXISTS idx_user_email ON notes(user_email);
        CREATE INDEX IF NOT EXISTS idx_created_at ON notes(created_at DESC);
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Database initialized successfully")

if __name__ == '__main__':
    init_database()
