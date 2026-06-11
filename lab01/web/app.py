import os
import re
import sqlite3
import subprocess
import hashlib
import urllib.parse
import importlib.util
import time
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, g, send_file, abort, make_response

app = Flask(__name__)
app.secret_key = 'bot2root-ctf-secret-key-2026'

DB_PATH = '/app/data/bot2root.db'
UPLOAD_DIR = '/app/uploads'

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Instance identity — set via env vars in docker-compose per user
INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'demo')
INSTANCE_IP   = os.environ.get('INSTANCE_IP', 'localhost')
PORT_WEB      = os.environ.get('PORT_WEB', '80')
PORT_NGINX    = os.environ.get('PORT_NGINX', '8080')
PORT_FTP      = os.environ.get('PORT_FTP', '21')
PORT_SSH      = os.environ.get('PORT_SSH', '2222')
PORT_IKE      = os.environ.get('PORT_IKE', '500')
PORT_SMB      = os.environ.get('PORT_SMB', '445')

# =============================================================
# RATE LIMITING — 10 requests per IP, bypass via X-Forwarded-For
# =============================================================
rate_limit_store = {}
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60


def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr


def check_rate_limit():
    ip = get_client_ip()
    now = time.time()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(rate_limit_store[ip]) >= RATE_LIMIT_MAX:
        return True
    rate_limit_store[ip].append(now)
    return False


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/scope')
def scope():
    info = {
        'ports': [PORT_WEB, PORT_NGINX, PORT_FTP, PORT_SSH, PORT_IKE, PORT_SMB],
    }
    return render_template('scope.html', info=info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if check_rate_limit():
            remaining = RATE_LIMIT_WINDOW
            flash(f'Rate limit exceeded. Try again in {remaining}s. '
                  f'Hint: This endpoint is accessible from internal network.', 'danger')
            return render_template('login.html', rate_limited=True), 429

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        blocked_patterns = [
            r"(\bor\b\s+\d+\s*=\s*\d+)",
            r"(\bor\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(union\s+select)",
            r"(--\s*$)",
            r"(;\s*drop\b)", r"(;\s*delete\b)", r"(;\s*update\b)", r"(;\s*insert\b)",
            r"(\bexec\b)", r"(\bsleep\b)", r"(\bbenchmark\b)",
            r"(load_file)", r"(into\s+outfile)", r"(into\s+dumpfile)",
            r"(\bor\b\s*1)", r"(\bor\b\s*true)",
            r"(admin'\s*--)", r"(admin'\s*#)",
            r"('\s*or\s*')", r"(1'\s*or\s*'1'\s*=\s*'1)", 
        ]

        input_check = (username + password).lower()
        for pattern in blocked_patterns:
            if re.search(pattern, input_check, re.IGNORECASE):
                flash('Suspicious input detected. Request blocked by WAF.', 'danger')
                return render_template('login.html')

        hashed_password = hashlib.md5(password.encode()).hexdigest()
        query = f"SELECT * FROM users WHERE (username='{username}' AND password='{hashed_password}')"

        try:
            db = get_db()
            result = db.execute(query).fetchone()
            if result:
                session['user_id'] = result['id']
                session['username'] = result['username']
                session['role'] = result['role']
                flash('Login successful! FLAG{b2r_sqli_waf_bypass_4a7c}', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials.', 'danger')
        except Exception:
            flash('Authentication error.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return render_template('home.html', user=user)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    if request.method == 'POST':
        new_name = request.form.get('name', '')
        db.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, session['user_id']))
        db.commit()
        flash('Profile updated!', 'success')
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)


@app.route('/blog')
@login_required
def blog_list():
    db = get_db()
    blogs = db.execute("""
        SELECT blogs.*, users.name as author_name, users.username as author_username
        FROM blogs JOIN users ON blogs.author_id = users.id
        ORDER BY created_at DESC
    """).fetchall()
    return render_template('blog_list.html', blogs=blogs)


@app.route('/blog/<int:blog_id>')
@login_required
def blog_detail(blog_id):
    db = get_db()
    blog = db.execute("""
        SELECT blogs.*, users.name as author_name, users.username as author_username
        FROM blogs JOIN users ON blogs.author_id = users.id
        WHERE blogs.id = ?
    """, (blog_id,)).fetchone()
    if not blog:
        abort(404)
    return render_template('blog_detail.html', blog=blog)


@app.route('/blog/<int:blog_id>/author')
@login_required
def blog_author_info(blog_id):
    db = get_db()
    blog = db.execute("""
        SELECT blogs.*, users.name as author_name, users.username as author_username,
               users.email as author_email, users.bio as author_bio
        FROM blogs JOIN users ON blogs.author_id = users.id
        WHERE blogs.id = ?
    """, (blog_id,)).fetchone()
    if not blog:
        abort(404)
    resp = make_response(render_template('blog_author.html', blog=blog))
    resp.set_cookie('secret_token', 'FLAG{b2r_stored_dom_xss_8e2f}', httponly=False, samesite='Lax', path='/')
    return resp


@app.route('/upload', methods=['GET'])
@login_required
def upload_page():
    db = get_db()
    uploads = db.execute("SELECT * FROM uploads WHERE user_id = ? ORDER BY uploaded_at DESC",
                         (session['user_id'],)).fetchall()
    return render_template('upload.html', uploads=uploads)


@app.route('/upload/check', methods=['POST'])
@login_required
def upload_check():
    filename = request.form.get('filename', '') or (request.json or {}).get('filename', '')
    if not filename:
        return jsonify({'status': 'error', 'message': 'No filename provided'}), 400
    basename = os.path.basename(filename)
    allowed_exts = ('.png', '.jpg', '.jpeg', '.pdf')
    if not basename.lower().endswith(allowed_exts):
        return jsonify({'status': 'error', 'message': 'Only image files (PNG, JPG, PDF) are accepted.'}), 400
    return jsonify({'status': 'ok', 'message': 'Filename accepted', 'filename': basename})


@app.route('/upload/send', methods=['POST'])
@login_required
def upload_send():
    file_obj = request.files.get('file')
    filename = request.form.get('filename', '')
    if not file_obj:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    basename = os.path.basename(filename) if filename else file_obj.filename
    if not basename:
        return jsonify({'status': 'error', 'message': 'No filename'}), 400
    allowed_exts = ('.png', '.jpg', '.jpeg', '.pdf')
    if not basename.lower().endswith(allowed_exts):
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400
    file_obj.seek(0)
    header = file_obj.read(8)
    file_obj.seek(0)
    PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
    JPG_MAGIC = b'\xff\xd8\xff'
    PDF_MAGIC = b'%PDF'
    valid_magic = (header[:8] == PNG_MAGIC or header[:3] == JPG_MAGIC or header[:4] == PDF_MAGIC)
    if not valid_magic:
        return jsonify({'status': 'error', 'message': 'Invalid file signature.'}), 400
    save_path = os.path.join(UPLOAD_DIR, basename)
    save_path = os.path.normpath(save_path)
    if not save_path.startswith(UPLOAD_DIR):
        return jsonify({'status': 'error', 'message': 'Invalid path'}), 400
    file_obj.save(save_path)
    db = get_db()
    db.execute("INSERT INTO uploads (user_id, filename, filepath) VALUES (?, ?, ?)",
               (session['user_id'], basename, save_path))
    db.commit()
    return jsonify({'status': 'ok', 'message': 'File uploaded successfully', 'filepath': basename})


@app.route('/upload/rename', methods=['POST'])
@login_required
def upload_rename():
    old_name = request.form.get('old', '') or (request.json or {}).get('old', '')
    new_name = request.form.get('new', '') or (request.json or {}).get('new', '')
    if not old_name or not new_name:
        return jsonify({'status': 'error', 'message': 'Missing old or new filename'}), 400
    old_name = os.path.basename(old_name)
    new_name = os.path.basename(new_name)
    old_path = os.path.normpath(os.path.join(UPLOAD_DIR, old_name))
    new_path = os.path.normpath(os.path.join(UPLOAD_DIR, new_name))
    if not old_path.startswith(UPLOAD_DIR) or not new_path.startswith(UPLOAD_DIR):
        return jsonify({'status': 'error', 'message': 'Invalid path'}), 400
    if not os.path.exists(old_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    os.rename(old_path, new_path)
    db = get_db()
    db.execute("UPDATE uploads SET filename = ?, filepath = ? WHERE filepath = ? AND user_id = ?",
               (new_name, new_path, old_path, session['user_id']))
    db.commit()
    return jsonify({'status': 'ok', 'message': f'Renamed to {new_name}'})


@app.route('/upload/view', methods=['GET'])
@login_required
def upload_view():
    filename = request.args.get('filepath', '')
    if not filename:
        return jsonify({'status': 'error', 'message': 'No filepath specified'}), 400
    file_path = os.path.normpath(os.path.join(UPLOAD_DIR, os.path.basename(filename)))
    if not file_path.startswith(UPLOAD_DIR):
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    return send_file(file_path)


@app.route('/upload/process', methods=['GET'])
@login_required
def upload_process():
    fname = request.args.get('name', '')
    cmd = request.args.get('cmd', '')
    if not fname:
        return jsonify({'status': 'error', 'message': 'Missing file name',
                        'usage': '/upload/process?name=<filename>&cmd=<command>'}), 400
    target_path = os.path.join(UPLOAD_DIR, os.path.basename(fname))
    target_path = os.path.normpath(target_path)
    if not target_path.startswith(UPLOAD_DIR):
        return jsonify({'status': 'error', 'message': 'Invalid path'}), 400
    if not os.path.exists(target_path):
        return jsonify({'status': 'error', 'message': 'File not found for processing'}), 404

    if target_path.endswith('.py') and cmd:
        allowed_commands = ['env', 'printenv', 'whoami', 'id', 'ls', 'cat', 'hostname']
        base_cmd = cmd.strip().split()[0] if cmd.strip() else ''
        if base_cmd not in allowed_commands:
            return jsonify({'status': 'error',
                            'message': f'Command "{base_cmd}" not allowed. Allowed: {", ".join(allowed_commands)}'}), 403
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10,
                                    cwd=UPLOAD_DIR, env={**os.environ})
            return jsonify({'status': 'ok', 'command': cmd, 'output': result.stdout, 'errors': result.stderr})
        except subprocess.TimeoutExpired:
            return jsonify({'status': 'error', 'message': 'Command timed out'}), 408
        except Exception:
            return jsonify({'status': 'error', 'message': 'Execution error'}), 500

    if target_path.endswith('.py'):
        try:
            spec = importlib.util.spec_from_file_location("resume_module", target_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return jsonify({'status': 'ok', 'message': 'Resume processed successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Processing error: {str(e)}'}), 500

    return jsonify({'status': 'error', 'message': 'File is not a processable resume format. Rename to a whitelisted extension to enable processing.'}), 422


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
