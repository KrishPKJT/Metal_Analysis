from flask import Flask, render_template, request, redirect, url_for,jsonify,request,session
import os
from db import Config 
from datetime import timedelta
from model.models import *
from routes.dashboard import dashboard_bp
from routes.login import login_bp
from routes.masters import masters_bp
from routes.parts import parts_bp
from routes.scan import scan_bp
from routes.users import users_bp
from routes.logs import logs_bp
from routes.reports import reports_bp

app = Flask(__name__)
app.secret_key = 'sZwbwVx5uv'
app.permanent_session_lifetime = timedelta(minutes=600)
app.config.from_object(Config)
db.init_app(app)
allowed_routes = ['login.login','login.checklogin', 'static','uploads']
@app.before_request
def check_session(): 
    if 'username' not in session and request.endpoint not in allowed_routes:
       if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
            return jsonify({'message': 'Session expired', 'redirect': url_for('login.login')}), 401
       else:
            return redirect(url_for('login.login'))
       
    
app.register_blueprint(dashboard_bp)
app.register_blueprint(login_bp)
app.register_blueprint(masters_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(parts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(reports_bp)
with app.app_context():
        db.create_all()    

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True,host='0.0.0.0', port=5000,ssl_context=('cert.pem', 'key.pem'))

