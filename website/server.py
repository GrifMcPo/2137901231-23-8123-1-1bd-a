from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BANS_FILE = os.path.join(DATA_DIR, 'bans.json')

os.makedirs(DATA_DIR, exist_ok=True)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Валидация
    if len(data.get('id', '')) > 8:
        return jsonify({'error': 'ID не должен превышать 8 символов'}), 400
    
    users = load_users()
    
    # Проверка на существование
    for user_id, user_data in users.items():
        if user_data['nick'] == data['nick']:
            return jsonify({'error': 'Ник уже существует'}), 400
        if user_data['id'] == data['id']:
            return jsonify({'error': 'ID уже существует'}), 400
        if user_data['username'] == data['username']:
            return jsonify({'error': 'Юзнейрм уже существует'}), 400
        if user_data['email'] == data['email']:
            return jsonify({'error': 'Почта уже используется'}), 400
    
    # Сохраняем пользователя
    user_id = data['id']
    users[user_id] = {
        'nick': data['nick'],
        'id': data['id'],
        'username': data['username'],
        'email': data['email'],
        'password': hash_password(data['password']),
        'ip': request.remote_addr,
        'registered_at': datetime.now().isoformat()
    }
    
    save_users(users)
    
    # Создаем сессию
    session_data = {
        'nick': data['nick'],
        'id': data['id'],
        'username': data['username'],
        'email': data['email'],
        'ip': request.remote_addr,
        'password': data['password']
    }
    
    return jsonify({'success': True, 'user': session_data})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()
    
    # Ищем пользователя по нику, id или юзнейрму
    user = None
    user_id = None
    
    for uid, user_data in users.items():
        if (user_data['nick'] == data['login'] or 
            user_data['id'] == data['login'] or 
            user_data['username'] == data['login']):
            user = user_data
            user_id = uid
            break
    
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    if user['password'] != hash_password(data['password']):
        return jsonify({'error': 'Неверный пароль'}), 401
    
    # Обновляем IP
    user['ip'] = request.remote_addr
    users[user_id] = user
    save_users(users)
    
    session_data = {
        'nick': user['nick'],
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'ip': request.remote_addr,
        'password': data['password']
    }
    
    return jsonify({'success': True, 'user': session_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
