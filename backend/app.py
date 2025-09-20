from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app)

# Register blueprints
from routers.auth_routes import auth_bp
app.register_blueprint(auth_bp)

# Initialize error handlers
from middlewares.error_handler import init_error_handlers
init_error_handlers(app)

# Auto-create tables
with app.app_context():
    db.create_all()

import os
from flask import send_from_directory, redirect

# Path to frontend directory (relative to backend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

# Root route: Redirect to register page
@app.route('/')
def root():
    return redirect('/register')

# Route to serve register.html
@app.route('/register')
def serve_register():
    return send_from_directory(FRONTEND_DIR, 'register.html')

# Route to serve login.html
@app.route('/login')
def serve_login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

# Route to serve index.html (welcome page)
@app.route('/index')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Routes to serve static assets
@app.route('/script.js')
def serve_script():
    return send_from_directory(FRONTEND_DIR, 'script.js')

@app.route('/styles.css')
def serve_styles():
    return send_from_directory(FRONTEND_DIR, 'styles.css')

if __name__ == '__main__':
    app.run(debug=True)