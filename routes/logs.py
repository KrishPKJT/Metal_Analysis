from flask import Blueprint, render_template,session,redirect,request,jsonify
from model.models import *
from helpers.masters_helper import *
import json

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
def logs():
    return render_template('logs.html')
@logs_bp.route('/list-view')
def list_view():
    return render_template('list_view.html')

@logs_bp.route('/logs/get-list',methods=['POST'])
def getLogList():
    limit = request.args.get('length', default=10, type=int)
    offset = request.args.get('start', default=0, type=int)
    
    logs_with_employee_info = db.session.query(
        Employees_log,
        Employees.name,
        Employees.gender,
        Buildings.building_name,
        Floors.floor_name,
        Stations.station_name
    ).join(Employees, Employees.employee_number == Employees_log.employee_number).join(Buildings,Buildings.id==Employees_log.building).join(Floors,Floors.id==Employees_log.floor).join(Stations,Stations.id==Employees_log.station).limit(limit).offset(offset).all()

    results = []
    for log, name, gender,building_name,floor_name,station_name in logs_with_employee_info:
        results.append({
            'log_id': log.id,
            'number': log.employee_number,
            'shift': getShiftById(log.shift),
            'building': building_name,
            'floor': floor_name,
            'status': log.status,
            'station': station_name,
            'log_date_time': log.log_date_time,
            'name': name,
            'gender': gender
        })
    
    userData = {
        "draw": 1,               
        "recordsTotal": 100,    
        "recordsFiltered": 100, 
        "data":results
    }

    return jsonify(userData)

@logs_bp.route('/view-log/',methods=['GET'])
def view_log():
    log_id = request.args.get('id')
    return render_template('scan.html',log_id=log_id)

@logs_bp.route("/get-log-details")
def get_log_details():
    log_id = request.args.get('id')
    result = db.session.query(Employees_log, Employees).join(
        Employees, Employees.employee_number == Employees_log.employee_number
    ).filter(Employees_log.id == log_id).first()
    employee_log, employee = result
    bObjects = []
    objects = json.loads(employee_log.objects)
    # print(objects)
    # if isinstance(objects, dict):
    #     print('yesd')
    if isinstance(objects, list):
        #print('yesl')
        for item in objects:
            id_list = [int(id.strip()) for id in item['o'].split(',')]
            results = Objectmappings.query.filter(Objectmappings.id.in_(id_list)).all()
            object_names = [obj.object_name for obj in results]
            object_names_str = ', '.join(object_names)
            bObjects.append({'p':item['p'],'g':getBodyPartsById(item['g']),'o':object_names_str})
            
    result = {
            "log_id": employee_log.id,
            "employee_number": employee_log.employee_number,
            "points": employee_log.points,
            "objects": employee_log.objects,
            "log_date_time": employee_log.log_date_time,
            "employee_name": employee.name,
            "employee_gender": employee.gender,
            "image":employee.image,
            'bObjects':bObjects,
            'shift':getShiftById(employee_log.shift),
            'building':getBuildingNameById(employee_log.building),
            'floor':getFloorNameById(employee_log.floor),
            'station':getStationNameById(employee_log.station),
            'medical_implants':employee.medical_implants,
            'medical_implants_position':employee.medical_implants_position,
            
        }
    return jsonify(result)


