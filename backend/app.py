from flask import Flask, send_from_directory, redirect
from flask_cors import CORS
from config import Config
from flask_mail import Mail
from database import init_db
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'))
app.config.from_object(Config)
# db = SQLAlchemy(app)
init_db(app)
 # Added after db initialization
CORS(app)
mail = Mail(app)  # Initialize Flask-Mail

# Register blueprints
from routers.auth_routes import auth_bp
app.register_blueprint(auth_bp)

# Register work order routes
from routers.wo_routes import wo_bp
app.register_blueprint(wo_bp, url_prefix='/api')

# Register new admin routes for protected admin actions
from routers.admin_routes import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Register user routes
from routers.user_routes import user_bp
app.register_blueprint(user_bp, url_prefix='/api')

# Register manufacturing order routes
from routers.mo_routes import mo_bp
app.register_blueprint(mo_bp, url_prefix='/api')

# Register product routes
from routers.product_routes import product_bp
app.register_blueprint(product_bp, url_prefix='/api')

# Register BOM routes
from routers.bom_routes import bom_bp
app.register_blueprint(bom_bp, url_prefix='/api')

# Register inventory routes
from routers.inventory_routes import inventory_bp
app.register_blueprint(inventory_bp, url_prefix='/api')

# Register stock ledger routes
from routers.stock_ledger_routes import stock_ledger_bp
app.register_blueprint(stock_ledger_bp, url_prefix='/api')

# Register work center routes
from routers.wc_routes import wc_bp
app.register_blueprint(wc_bp, url_prefix='/api')

# Register report routes
from routers.report_routes import report_bp
app.register_blueprint(report_bp, url_prefix='/api')

# Initialize error handlers
from middlewares.error_handler import init_error_handlers
init_error_handlers(app)

# MongoDB doesn't need table creation like SQLAlchemy
# Collections are created automatically when first used

# Path to frontend directory (relative to backend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

# Root route: Redirect to login page
@app.route('/')
def root():
    return redirect('/login')

# Route to serve login.html
@app.route('/login')
def serve_login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

# Route to serve index.html (welcome page)
@app.route('/index')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Route to serve forgot_password.html
@app.route('/forgot-password')
def serve_forgot_password():
    return send_from_directory(FRONTEND_DIR, 'forgot_password.html')

# New routes for remaining frontend pages
@app.route('/bom')
def serve_bom():
    return send_from_directory(FRONTEND_DIR, 'bom_list.html')

@app.route('/bom-form')
def serve_bom_form():
    return send_from_directory(FRONTEND_DIR, 'bom_form.html')

@app.route('/bom-list')
def serve_bom_list():
    return send_from_directory(FRONTEND_DIR, 'bom_list.html')

@app.route('/inventory')
def serve_inventory():
    return send_from_directory(FRONTEND_DIR, 'inventory.html')

@app.route('/mo')
def serve_mo():
    return send_from_directory(FRONTEND_DIR, 'mo.html')

@app.route('/mo-detail')
def serve_mo_detail():
    return send_from_directory(FRONTEND_DIR, 'mo_detail.html')

@app.route('/mo-form')
def serve_mo_form():
    return send_from_directory(FRONTEND_DIR, 'mo_create.html')

@app.route('/product-list')
def serve_product_list():
    return send_from_directory(FRONTEND_DIR, 'product_list.html')

@app.route('/profile')
def serve_profile():
    return send_from_directory(FRONTEND_DIR, 'profile.html')

@app.route('/reports')
def serve_reports():
    return send_from_directory(FRONTEND_DIR, 'reports.html')

@app.route('/stock-ledger')
def serve_stock_ledger():
    return send_from_directory(FRONTEND_DIR, 'stock_ledger.html')


@app.route('/wo')
def serve_wo():
    return send_from_directory(FRONTEND_DIR, 'wo_list.html')

@app.route('/wo-list')
def serve_wo_list():
    return send_from_directory(FRONTEND_DIR, 'wo_list.html')

@app.route('/wo_list')
def serve_wo_list_underscore():
    return send_from_directory(FRONTEND_DIR, 'wo_list.html')

@app.route('/users')
def serve_users():
    return send_from_directory(FRONTEND_DIR, 'users.html')

@app.route('/wo-task')
def serve_wo_task():
    return send_from_directory(FRONTEND_DIR, 'wo_task.html')

@app.route('/bom-create')
def serve_bom_create():
    return send_from_directory(FRONTEND_DIR, 'bom_create.html')

@app.route('/product-master')
def serve_product_master():
    return send_from_directory(FRONTEND_DIR, 'product_master.html')

@app.route('/settings')
def serve_settings():
    return send_from_directory(FRONTEND_DIR, 'settings.html')

# Work Center routes
@app.route('/wc-list')
def serve_wc_list():
    return send_from_directory(FRONTEND_DIR, 'wc_list.html')

@app.route('/wc-create')
def serve_wc_create():
    return send_from_directory(FRONTEND_DIR, 'wc_create.html')

@app.route('/wc-detail')
def serve_wc_detail():
    return send_from_directory(FRONTEND_DIR, 'wc_detail.html')

# Route to serve navbar component
@app.route('/components/navbar.html')
def serve_navbar():
    return send_from_directory(FRONTEND_DIR, 'components/navbar.html')

# General route to serve any component files
@app.route('/components/<path:filename>')
def serve_components(filename):
    return send_from_directory(FRONTEND_DIR, 'components', filename)

# Route to serve JavaScript files from js directory
@app.route('/js/<path:filename>')
def serve_js(filename):
    print(f"Serving JS file: {filename}")
    return send_from_directory(FRONTEND_DIR, f'js/{filename}')

# Route to serve CSS files
@app.route('/styles.css')
def serve_styles_css():
    return send_from_directory(FRONTEND_DIR, 'styles.css')

@app.route('/style.css')
def serve_style_css():
    return send_from_directory(FRONTEND_DIR, 'style.css')

# Route to serve main script.js
@app.route('/script.js')
def serve_script_js():
    return send_from_directory(FRONTEND_DIR, 'script.js')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, use_reloader=False)