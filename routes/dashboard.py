from flask import Blueprint, render_template,session,redirect,request,jsonify
from model.models import *
from datetime import datetime
from sqlalchemy import cast, func,Integer,text
import json
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
      return render_template('dashboard.html')
@dashboard_bp.route('/log/get-list', methods=['GET'])
def getEmpLogList():    
      query = db.session.query(
        Employees_log.id,
        Employees_log.employee_number,
        Employees.name.label('employee_name'),
        Employees.gender.label('employee_gender'),
        Employees_log.building,
        Employees_log.floor,
        Employees_log.station,
        Buildings.building_name,
        Floors.floor_name,
        Stations.station_name,
        Employees_log.log_date_time,
        Employees_log.status,
        Employees_log.shift,       
        Employees_log.objects       
    ).join(Employees, Employees_log.employee_number == Employees.employee_number)\
     .join(Buildings, cast(Employees_log.building, Integer) == Buildings.id)\
     .join(Floors, cast(Employees_log.floor, Integer) == Floors.id)\
     .join(Stations, cast(Employees_log.station, Integer) == Stations.id)
    
      role = session.get('role')
      logged_user = session.get('logged_user') 
      
      today = datetime.today().date()   
      total_query = query.filter(Employees_log.log_date_time.like(f'{today} %'))
      in_total_query = query.filter(Employees_log.log_date_time.like(f'{today} %'),Employees_log.status=='in')
      out_total_query = query.filter(Employees_log.log_date_time.like(f'{today} %'),Employees_log.status=='out')

      if role!="admin":
          in_total_query = in_total_query.filter(Employees_log.created_by==logged_user )
          out_total_query = out_total_query.filter(Employees_log.created_by==logged_user)
          
     
      total_records= total_query.count()  
      total_records_in = in_total_query.count()
      total_records_out= out_total_query.count()

      logData = {
        "total_records": total_records,   
        "in": total_records_in,                      
        "out": total_records_out,     
                 
    }

      return jsonify(logData)

def prepare_logs(result):
    shift_mapping = {
        'S1': 'Shift 1',
        'S2': 'Shift 2',
        'S3': 'Shift 3',
        'S4': 'Shift 4'
    }
    body_parts = {bp.id: bp.body_parts_name for bp in Bodyparts.query.all()}
    objects = {obj.id: obj.object_name for obj in Objectmappings.query.all()}
    logs = []
    
    for log in result:
        shift_full_name = shift_mapping.get(log.shift, log.shift)  # Get shift name or default to original
        try:
            objects_data = json.loads(log.objects)  # Parse the objects JSON
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding JSON for log {log.id}: {e}")
            objects_data = []  # Set to empty list in case of error
        
        body_part_map = {}

        for item in objects_data:
            body_part_id = item.get('g')  # Get body part ID
            object_ids = item.get('o', '').split(',')  # Split object IDs (comma-separated)
            
            # Strip any extra spaces from object IDs
            object_ids = [obj_id.strip() for obj_id in object_ids if obj_id.strip()]
            
            body_part_name = body_parts.get(body_part_id, "Unknown")
            object_names = [objects.get(int(obj_id), "Unknown") for obj_id in object_ids]

            if body_part_name not in body_part_map:
                body_part_map[body_part_name] = []
            body_part_map[body_part_name].extend(object_names)

        # Build the output for metal exceptions
        body_parts_output = []
        for bp_name, obj_names in body_part_map.items():
            objects_str = ', '.join(sorted(set(obj_names)))  # Use set to avoid duplicates, sorted for consistency
            body_parts_output.append(f"{bp_name}: {objects_str}")

       
        logs.append({
            
            'Building': log.building_name,
            'Floor': log.floor_name,
            'Station': log.station_name,
            'Date_Time': log.log_date_time,
            'Transaction': log.status,
            'EmpID': log.employee_number,
            'EmployeeName': log.employee_name,
            'Gender': log.employee_gender,
            'Shift': shift_full_name,
            'TypeOfMetalExceptions': ' | '.join(body_parts_output)
        })

    return logs