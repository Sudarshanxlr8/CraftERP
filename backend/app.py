from routers.bom_routes import bom_bp
app.register_blueprint(bom_bp, url_prefix='/api')