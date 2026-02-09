#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv




print("🐍 Python version:", sys.version)
print("📁 Current directory:", os.getcwd())
print("📄 Files in directory:", os.listdir('.'))

# Load .env
print("\n🔍 Loading .env file...")
dotenv_result = load_dotenv()
print(f"✅ .env loaded: {dotenv_result}")

# Check DATABASE_URL
db_url = os.environ.get('DATABASE_URL')
print(f"\n🔗 DATABASE_URL: {'✅ FOUND' if db_url else '❌ MISSING'}")
if db_url:
    # Hide password for security
    hidden_url = db_url.split('@')[0] + '@***HIDDEN***'
    print(f"   {hidden_url}")

try:
    print("\n🧪 Testing database connection...")
    import psycopg2
    
    conn = psycopg2.connect(db_url)
    print("✅ Connection successful!")
    
    cur = conn.cursor()
    
    # Create table if needed
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255),
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Table ready")
    
    # Count notes
    cur.execute('SELECT COUNT(*) FROM notes')
    count = cur.fetchone()[0]
    print(f"📊 Found {count} notes")
    
    # Show recent notes
    cur.execute('SELECT id, user_email, LEFT(note_text, 50) as preview, created_at FROM notes ORDER BY created_at DESC LIMIT 3')
    recent = cur.fetchall()
    print("\n📝 Recent notes:")
    for note in recent:
        print(f"   ID {note[0]}: {note[1]} - {note[2]}...")
    
    cur.close()
    conn.close()
    print("\n🎉 Everything working perfectly!")
    
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("💡 Run: pip install psycopg2-binary python-dotenv")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
