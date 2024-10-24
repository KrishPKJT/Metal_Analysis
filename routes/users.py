from flask import Blueprint, render_template,session,redirect,request,jsonify
from sqlalchemy import asc

from model.models import *
from werkzeug.security import generate_password_hash,check_password_hash
users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
def users():
    return render_template('users.html')

@users_bp.route('/users/statusUpdate',methods=['POST'])
def userStatusUpdate():
    user = Users.query.filter_by(id=request.form.get('id')).update({"status":request.form.get('status')})
    db.session.commit()
    if user:
        return jsonify({'status':'ok'})
    else:
        return jsonify({'status':'failed'})

@users_bp.route('/users/get-user-data/<int:id>',methods=['get'])
def getUserData(id):
    user = Users.query.get(id)
    if user:
        user = {'id': user.id, 'name': user.name,'username': user.username, 'role': user.role,'rights':user.rights}
        return jsonify({'status': 'ok', 'user': user})
    else:
        return jsonify({'status': 'failed'})
@users_bp.route('/users/get-list',methods=['POST'])
def getUserList():
    limit = request.args.get('length', default=10, type=int)
    offset = request.args.get('start', default=0, type=int)
    
    users = Users.query.order_by(asc(Users.name)).offset(offset).limit(limit).all()
    users_list = [{'id': user.id, 'name': user.name, 'username': user.username, 'role': user.role, 'last_login': user.lastLogin.isoformat() if user.lastLogin else None,'status':user.status} for user in users]
    
    userData = {
        "draw": 1,               
        "recordsTotal": 100,    
        "recordsFiltered": 100, 
        "data":users_list
    }

    return jsonify(userData)

@users_bp.route('/users/save',methods=['POST'])
def saveUser():
    if request.form.get('id')=="":
        user = Users(name=request.form.get('name'), username=request.form.get('username'),password=generate_password_hash(request.form.get('password')),role=request.form.get('role'),rights=request.form.get('rights'),createdAt=get_current_time(),status='enable')
        db.session.add(newUser)
    else:
        updateData = {"name":request.form.get('name'), "username":request.form.get('username'),"role":request.form.get('role'),"rights":request.form.get('rights'),"createdAt":get_current_time()}
        if request.form.get('password')!="":
            updateData['password'] = generate_password_hash(request.form.get('password'))
            
        user =  Users.query.filter_by(id=request.form.get('id')).update(updateData)
    db.session.commit()
    if user:
        return jsonify({'status':'ok'})
    else:
        return jsonify({'status':'failed'})
