import sqlite3
import os
import hashlib

DB_PATH = '/app/data/bot2root.db'

def init_db():
    if os.path.exists(DB_PATH):
        return
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            name TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            bio TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    admin_pass = hashlib.md5('S3cur3P@ssw0rd!2026#Bot2Root'.encode()).hexdigest()
    db.execute("INSERT INTO users (username, password, email, name, role) VALUES (?, ?, ?, ?, ?)",
               ('admin', admin_pass, 'admin@bot2root.website', 'Administrator', 'admin'))
    db.execute("INSERT INTO blogs (title, content, author_id) VALUES (?, ?, ?)",
               ('Welcome to Bot2Root', 'This is the official Bot2Root CTF platform. Good luck hacking!', 1))
    db.execute("INSERT INTO blogs (title, content, author_id) VALUES (?, ?, ?)",
               ('Security Best Practices',
                'Always validate user input. Never trust the client side. Use parameterized queries. '
                'Remember: output encoding is just as important as input validation. '
                'Check how user-controlled data flows through the application — from storage to rendering.', 1))
    db.execute("INSERT INTO blogs (title, content, author_id) VALUES (?, ?, ?)",
               ('Network Fundamentals', 'Understanding TCP/IP, ports, and protocols is essential for penetration testing.', 1))
    db.commit()
    db.close()

if __name__ == '__main__':
    init_db()
    print("[+] Database initialized successfully")
