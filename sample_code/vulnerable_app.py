#!/usr/bin/env python3
"""
Sample vulnerable Python application for testing the Cerebras Code Scanner.

This file contains intentional security vulnerabilities and performance issues
to demonstrate the capabilities of the scanner.
"""

import os
import sqlite3
import pickle
import yaml
import hashlib
import random
from flask import Flask, request, render_template_string

# Hardcoded credentials (security flaw)
DB_USER = "admin"
DB_PASSWORD = "password123"
API_KEY = "sk_live_51HV2nSJMcbXXXXXXXXXXXXXXX"

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Vulnerable App!"

# SQL Injection vulnerability
@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    return str(user)

# Command injection vulnerability
@app.route('/ping')
def ping():
    hostname = request.args.get('host', 'localhost')
    
    # Vulnerable to command injection
    result = os.system(f"ping -c 1 {hostname}")
    
    return f"Ping result: {result}"

# Unsafe deserialization
@app.route('/load_data')
def load_data():
    data_file = request.args.get('file', 'data.pickle')
    
    try:
        with open(data_file, 'rb') as f:
            # Vulnerable to pickle deserialization attacks
            data = pickle.load(f)
        return str(data)
    except Exception as e:
        return f"Error: {str(e)}"

# Unsafe YAML loading
@app.route('/config')
def load_config():
    config_file = request.args.get('file', 'config.yaml')
    
    try:
        with open(config_file, 'r') as f:
            # Vulnerable to YAML deserialization attacks
            config = yaml.load(f)
        return str(config)
    except Exception as e:
        return f"Error: {str(e)}"

# Cross-Site Scripting (XSS) vulnerability
@app.route('/message')
def message():
    user_message = request.args.get('message', 'Hello!')
    
    # Vulnerable to XSS
    template = f"""<html>
    <head><title>Message</title></head>
    <body>
        <h1>Your Message</h1>
        <p>{user_message}</p>
    </body>
</html>"""
    
    return render_template_string(template)

# Weak cryptography
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Weak password hashing (MD5)
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    # Store user in database (simplified)
    return f"User {username} registered with hash {password_hash}"

# Insecure randomness
@app.route('/reset_password')
def reset_password():
    username = request.args.get('username')
    
    # Insecure random token generation
    token = str(random.randint(10000, 99999))
    
    return f"Password reset token for {username}: {token}"

# Path traversal vulnerability
@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    
    try:
        # Vulnerable to path traversal
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# Performance issue - inefficient nested loops (O(n²))
def find_duplicates(items):
    duplicates = []
    
    # Inefficient O(n²) algorithm
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    
    return duplicates

# Logical error - off-by-one
def get_last_n_items(items, n):
    # Off-by-one error
    return items[len(items) - n - 1:]

# Unhandled exceptions
@app.route('/divide')
def divide():
    a = int(request.args.get('a', '0'))
    b = int(request.args.get('b', '0'))
    
    # Missing exception handling for division by zero
    result = a / b
    
    return f"{a} / {b} = {result}"

if __name__ == '__main__':
    # Running in debug mode (security issue)
    app.run(debug=True, host='0.0.0.0')