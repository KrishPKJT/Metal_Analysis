from flask import Blueprint, render_template,session,redirect,request,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from model.models import *
import logging
login_bp = Blueprint('login', __name__)


@login_bp.route('/login')
def login():
      return render_template('login.html')

@login_bp.route('/')
def index():
     return render_template('login.html')

@login_bp.route("/checklogin",methods=['POST'])
def checklogin():
    user = Users.query.filter_by(username=request.form.get('username'),status='enable').first()
    if user and check_password_hash(user.password, request.form.get('password')):
        user.lastLogin = get_current_time()
        db.session.commit()
        session['logged_user'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['rights'] = user.rights
        if user.role=='admin':
            return redirect(url_for('dashboard.dashboard'))
        else:
            return redirect(url_for('login.selectShift'))
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('login.login'))
        

@login_bp.route("/selectShift",methods=['GET'])
def selectShift():
    if session['username']:
        session['shift'] = request.form.get('shift')
        session['building'] = request.form.get('building')
        session['floor'] = request.form.get('floor')
        session['station'] = request.form.get('station')
        logging.warning(f"Session contents: {session}")
        return render_template('shift_selection.html')
    else:
         return redirect(url_for('login.login'))

@login_bp.route("/setShift",methods=['POST'])
def setShift():
    if session['username']:
        session['shift'] = request.form.get('shift')
        session['building'] = request.form.get('building')
        session['floor'] = request.form.get('floor')
        session['station'] = request.form.get('station')
        logging.warning(f"Session contents: {session}")
        return redirect(url_for('dashboard.dashboard'))
    else:
         return redirect(url_for('login.login'))


@login_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('rights', None)
    session.pop('shift', None)
    session.pop('building', None)
    session.pop('floor', None)
    session.pop('station', None)
    return redirect(url_for('login.login'))