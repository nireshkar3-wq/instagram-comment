from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import os
import logging
import json
import shutil
from insta_bot import InstagramCommentBot

PROFILES_FILE = 'profiles.json'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'insta-secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

# Store the current bot instance and thread
bot_status = {
    'running': False,
    'current_task': None,
    'last_log': None
}
bot_thread = None

@app.route('/profiles', methods=['GET'])
def get_profiles():
    return jsonify(load_profiles())

@app.route('/profiles', methods=['POST'])
def add_profile():
    data = request.json
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    
    if not name or not username or not password:
        return jsonify({'error': 'All fields are required'}), 400
        
    profiles = load_profiles()
    profiles[name] = {
        'username': username,
        'password': password
    }
    save_profiles(profiles)
    return jsonify({'message': f'Profile {name} saved successfully'})

@app.route('/profiles/<name>', methods=['DELETE'])
def delete_profile(name):
    profiles = load_profiles()
    if name in profiles:
        # Delete from JSON
        del profiles[name]
        save_profiles(profiles)
        
        # Delete session directory if it exists
        session_dir = os.path.join('Instagram_session', name)
        if os.path.exists(session_dir):
            try:
                shutil.rmtree(session_dir)
                return jsonify({'message': f'Profile {name} and its session data deleted'})
            except Exception as e:
                return jsonify({'message': f'Profile {name} credentials deleted, but failed to remove session folder: {str(e)}'}), 200
        
        return jsonify({'message': f'Profile {name} credentials deleted'})
    return jsonify({'error': 'Profile not found'}), 404

def bot_log_callback(message, level):
    """Callback function for the bot to send logs to the frontend."""
    level_str = "INFO"
    if level == logging.ERROR: level_str = "ERROR"
    elif level == logging.WARNING: level_str = "WARNING"
    
    timestamp = time.strftime('%H:%M:%S')
    socketio.emit('bot_log', {
        'message': message,
        'level': level_str,
        'timestamp': timestamp
    })

def run_bot_task(post_url, comment, count, headless, profile_name, username, password):
    global bot_thread
    bot_status['running'] = True
    bot_status['current_task'] = f"Posting to {post_url} via {profile_name}"
    
    try:
        bot = InstagramCommentBot(
            headless=headless, 
            log_callback=bot_log_callback,
            profile_name=profile_name,
            username=username,
            password=password
        )
        success = bot.run(post_url, comment, count)
        
        if success:
            bot_log_callback("✅ Bot task completed successfully!", logging.INFO)
        else:
            bot_log_callback("❌ Bot task failed.", logging.ERROR)
            
    except Exception as e:
        bot_log_callback(f"Critical error: {str(e)}", logging.ERROR)
    finally:
        bot_status['running'] = False
        bot_status['current_task'] = None
        socketio.emit('bot_finished', {'success': True})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_bot():
    global bot_thread
    
    if bot_status['running']:
        return jsonify({'error': 'Bot is already running'}), 400
        
    data = request.json
    post_url = data.get('post_url')
    comment = data.get('comment')
    count = int(data.get('count', 1))
    headless = data.get('headless', False)
    profile_name = data.get('profile_name', 'default')
    
    # Load profile details if exists
    profiles = load_profiles()
    if profile_name in profiles:
        username = profiles[profile_name]['username']
        password = profiles[profile_name]['password']
        bot_log_callback(f"Using saved credentials for profile: {profile_name}", logging.INFO)
    else:
        username = data.get('username')
        password = data.get('password')
    
    if not post_url or not comment:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    bot_thread = threading.Thread(
        target=run_bot_task, 
        args=(post_url, comment, count, headless, profile_name, username, password)
    )
    bot_thread.daemon = True
    bot_thread.start()
    
    return jsonify({'message': 'Bot started successfully'})

@app.route('/status')
def get_status():
    return jsonify(bot_status)

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
