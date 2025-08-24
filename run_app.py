#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Flask Application Runner
"""
import os
import sys

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from flask import Flask, render_template, redirect, request, session, jsonify

# Create Flask app
app = Flask(__name__, 
            static_folder=os.path.join(ROOT_DIR, 'public/static'),
            template_folder=os.path.join(ROOT_DIR, 'public/Views'))

# Basic configuration
app.config.update({
    'SECRET_KEY': 'dev-secret-key-change-in-production',
    'DEBUG': True
})

# Routes
@app.route('/')
def index():
    """Redirect to login"""
    return redirect('/auth/login')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple demo authentication
        if email == 'admin@example.com' and password == 'password123':
            session['user_id'] = 1
            session['user_name'] = 'Admin'
            session['user_email'] = email
            return redirect('/dashboard')
        else:
            return render_template('auth/login.html', error='Invalid credentials')
    
    return render_template('auth/login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect('/auth/login')
    
    return render_template('home/dashboard.html')

@app.route('/auth/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect('/auth/login')

@app.route('/api/test')
def api_test():
    """Test API endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is working',
        'data': {
            'version': '1.0.0',
            'features': [
                'E-Commerce Integration',
                'AI Image Processing',
                'Payment Gateway',
                'Social Media Management'
            ]
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return "<h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p>", 404

@app.errorhandler(500)
def server_error(e):
    return "<h1>500 - Internal Server Error</h1><p>Something went wrong on the server.</p>", 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(os.path.join(ROOT_DIR, 'storage/sessions'), exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 PofuAI Application Starting...")
    print("="*60)
    print("📍 URL: http://localhost:5001")
    print("👤 Demo Login:")
    print("   Email: admin@example.com")
    print("   Password: password123")
    print("="*60 + "\n")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Run the app
    app.run(host=host, port=port, debug=debug)