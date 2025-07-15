from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
import os
import json
from datetime import datetime
import requests
from werkzeug.utils import secure_filename
import hashlib
from dotenv import load_dotenv

APP_TOKEN = os.getenv("APP_TOKEN")

app = Flask(__name__)
app.secret_key = APP_TOKEN

# Base path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
PROFILE_PIC_DIR = os.path.join(STATIC_DIR, 'profile_pics')

# File paths
LOGIN_DATA_FILE = os.path.join(DATA_DIR, 'logindata.json')
MESSAGE_DATA_FILE = os.path.join(DATA_DIR, 'messages.json')
REQUEST_LOG_FILE = os.path.join(DATA_DIR, 'request_logs.json')
USER_DATA_FILE = os.path.join(DATA_DIR, 'users.json')

# Upload config
app.config['UPLOAD_FOLDER'] = PROFILE_PIC_DIR
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



USE_TEST_IP = False
TEST_IP = '8.8.8.8'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_json_file(filepath, initial_data=None):
    """Ensure a JSON file exists with the given initial data type."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, 'w') as f:
            json.dump(initial_data if initial_data is not None else [], f)


def safe_load_json(filepath, fallback, encoding='utf-8'):
    """Safely load JSON and fallback if corrupted or wrong type."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if not isinstance(data, type(fallback)):
                raise ValueError("Incorrect JSON structure")
            return data
    except (json.JSONDecodeError, ValueError):
        return fallback


def log_request(method, endpoint):
    ip = TEST_IP if USE_TEST_IP else request.remote_addr
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        data = response.json()
        city = data.get('city', 'Unknown')
        state = data.get('region', 'Unknown')
        country = data.get('country', 'Unknown')
        zip_code = data.get('postal', 'Unknown')
        local_time = data.get('timezone', 'Unknown')
    except Exception as e:
        city = state = country = zip_code = local_time = 'Unknown'
        print(f"Error fetching IP info: {e}")

    log_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "method": method,
        "endpoint": endpoint,
        "ip": ip,
        "city": city,
        "state": state,
        "country": country,
        "zip": zip_code,
        "local_time": local_time
    }

    logs = safe_load_json(REQUEST_LOG_FILE, [])
    logs.append(log_entry)
    with open(REQUEST_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('send_message'))
    return redirect(url_for('login'))

# login and registration routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return "Missing username or password", 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        users = safe_load_json(USER_DATA_FILE, {})

        if username in users and users[username]['password'] == hashed_password:
            session['username'] = username
            session['profile_pic'] = users[username].get('profile_pic', '')
            return redirect(url_for('send_message'))

        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        profile_pic = request.files.get('profile_pic')

        users = safe_load_json(USER_DATA_FILE, {})

        if username in users:
            return render_template('register.html', error='Username already exists')

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        profile_pic_filename = ""

        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(f"{username}_{profile_pic.filename}")
            filepath = os.path.join(PROFILE_PIC_DIR, filename)
            profile_pic.save(filepath)
            profile_pic_filename = filename

        users[username] = {
            "password": hashed_password,
            "profile_pic": profile_pic_filename
        }

        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))
    


    messages = safe_load_json(MESSAGE_DATA_FILE, [], encoding='utf-8')

    if request.method == 'POST':
        profile_pic = session.get('profile_pic', '')
        new_message = {
            "username": session['username'],
            "message": request.form.get('message', ''),
            "profile_pic": profile_pic,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        messages.append(new_message)

        with open(MESSAGE_DATA_FILE, 'w') as f:
            json.dump(messages, f, indent=4)

        log_request('POST', '/send_message')
        return redirect(url_for('send_message'))

    log_request('GET', '/send_message')
    return render_template('chat.html',
                           messages=[(m['username'], m['message'], m.get('profile_pic', '')) for m in messages])


@app.route('/get_messages')
def get_messages():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    messages = safe_load_json(MESSAGE_DATA_FILE, [])
    return jsonify(messages=messages[-100:])


@app.route('/logout')
def logout():
    username = session.pop('username', None)
    session.pop('profile_pic', None)

    if username:
        log_request('GET', '/logout')
    return redirect(url_for('login'))


if __name__ == '__main__':
    
    from waitress import serve

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROFILE_PIC_DIR, exist_ok=True)

    # Correctly initialize all data files
    ensure_json_file(LOGIN_DATA_FILE, {})
    ensure_json_file(USER_DATA_FILE, {})
    ensure_json_file(MESSAGE_DATA_FILE, [])
    ensure_json_file(REQUEST_LOG_FILE, [])

    port = int(os.environ.get('PORT', 12345))
    serve(app, host='0.0.0.0', port=port)



# additiona comments for a commit