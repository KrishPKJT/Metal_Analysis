from flask import Blueprint, render_template,session,redirect,request,jsonify,send_file,url_for
from model.models import *
from sqlalchemy import cast, func,Integer,text
from sqlalchemy import not_, and_,or_,JSON
import json
from datetime import datetime
import pandas as pd
import json
from io import BytesIO
import logging
import xlsxwriter
import os

reports_bp = Blueprint('reports', __name__)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
@reports_bp.route('/reports')
def reports():
    return render_template('reports.html')
@reports_bp.route('/employee/emp_list', methods=['get'])
def getEmployeeList():
   employee_list = Employees.query.all()   
   employee_list = [{'id': employee.id, 'name': employee.name, 'employee_number': employee.employee_number,'gender': employee.gender} for employee in employee_list]
   return jsonify({'data': employee_list})

@reports_bp.route('/report/generated-report', methods=['POST'])
def get_employee_logs():
    reportType = request.form.get('reportType')
    fromdate=request.form.get('fromdate')
    todate=request.form.get('todate')
    selected_employees = request.form.get('selectedEmployees')
    selected_shifts = request.form.get('selectedShifts')
    selected_transaction = request.form.get('selectedEntries')
    selected_gender = request.form.get('selectedGenders')
    selected_year=request.form.get('selected_year')
    selected_build=request.form.get('selected_build')
    selected_floor=request.form.get('selected_floor')
    selected_station=request.form.get('selected_station')
    selected_objects=request.form.get('selected_objects')

    selected_build_all=request.form.get('selected_build_all')
    selected_floor_all=request.form.get('selected_floor_all')
    selected_station_all=request.form.get('selected_station_all')
    if selected_build_all:
        selected_build_all = json.loads(selected_build_all)
    if selected_floor_all:
        selected_floor_all = json.loads(selected_floor_all)
    if selected_station_all:
        selected_station_all = json.loads(selected_station_all)
    if selected_employees:
        selected_employees = json.loads(selected_employees)
    if selected_shifts:
        selected_shifts = json.loads(selected_shifts)
    if selected_transaction:
        selected_transaction = json.loads(selected_transaction)
    if selected_gender:
        selected_gender = json.loads(selected_gender)
    object_ids=[]
    if selected_objects:
        object_ids  = json.loads(selected_objects) if selected_objects else []
    
    

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

    today = datetime.today().date()
    output_dir = 'static/reports'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    current_datetime = datetime.today()
    current_datetime_str = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')

    report_name=f"{reportType}_{current_datetime_str}.xlsx"

    header_title = ''
    report_filename = os.path.join(output_dir, report_name)
    
    with pd.ExcelWriter(report_filename, engine='xlsxwriter') as writer:
        if reportType == 'Asondate':           
            sheet_name = 'As On Date'          
            query = query.filter(Employees_log.log_date_time.like(f'{today} %'))           
            result = query.all()
            today_date_str = today.strftime('%Y-%m-%d')
            if result:
                write_to_excel(writer, result, today_date_str)

        elif reportType == 'Monthondate':
            month_start = today.replace(day=1)
            query = apply_filters(query, month_start, today)
          
            for day in range(1, today.day + 1):
                date_str = today.replace(day=day).strftime("%d-%b-%Y")
                daily_query = query.filter(func.date(Employees_log.log_date_time) == today.replace(day=day))

                result = daily_query.all()
                if result:
                    write_to_excel(writer, result, date_str)

        elif reportType == 'Yearondate':
            year_start = today.replace(month=1, day=1)
            query = apply_filters(query, year_start, today)         
            for month in range(1, today.month + 1):
                month_start = today.replace(month=month, day=1)
                month_end = month_start.replace(day=1, month=month % 12 + 1)  
                month_str = month_start.strftime("%b-%Y")
                monthly_query = query.filter(func.date(Employees_log.log_date_time).between(month_start, month_end))
                result = monthly_query.all()
                if result:
                    write_to_excel(writer, result, month_str)  
                
        elif reportType == 'Datewise':  
            sheet_name='Datewise Report'        
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)
            result = query.all()        
            write_to_excel(writer, result, sheet_name)
        elif reportType == 'Employeewise':
            sheet_name='Employee wise'
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)
            result = query.all()
            write_to_excel(writer, result, sheet_name) 
        elif reportType == 'Monthwise':            
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)  
          
            for day in range(1, today.day + 1):
                date_str = today.replace(day=day).strftime("%d-%b-%Y")
                daily_query = query.filter(func.date(Employees_log.log_date_time) == today.replace(day=day))

                result = daily_query.all()
                if result:
                    write_to_excel(writer, result, date_str)  
        elif reportType == 'Yearwise':
            fromdate,todate=get_dates(selected_year)
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids) 
            records_found = False 
            for month in range(1, today.month + 1):
                month_start = today.replace(month=month, day=1)
                month_end = month_start.replace(day=1, month=month % 12 + 1)  
                month_str = month_start.strftime("%b-%Y")
                monthly_query = query.filter(func.date(Employees_log.log_date_time).between(month_start, month_end))
                result = monthly_query.all()
                if result:
                    write_to_excel(writer, result, month_str) 
                    records_found = True
              
        elif reportType == 'Shiftwise':
            sheet_name='Shift wise'
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)
            shift_mapping = {
                'S1': 'Shift 1',
                'S2': 'Shift 2',
                'S3': 'Shift 3',
                'S4': 'Shift 4'
            }
          
            for shift in selected_shifts:            
                shift_query = query.filter(Employees_log.shift == shift)
                result = shift_query.all() 
                   
                if result:  
                    sheet_name = shift_mapping.get(shift, shift)
                    write_to_excel(writer, result, sheet_name) 
        elif reportType == 'Genderwise':
            sheet_name='Gender wise'
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)
            for gender in selected_gender:            
                gender_query = query.filter(Employees.gender == gender)
                result = gender_query.all()              
                if result:  
                    sheet_name = gender 
                    write_to_excel(writer, result, sheet_name) 
        elif reportType == 'Transactionwise':
            sheet_name='Transaction wise'
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build_all,selected_floor_all,selected_station_all,object_ids)
           
            for status in selected_transaction:            
                transaction_query = query.filter(Employees_log.status == status)
                result = transaction_query.all()              
                if result:  
                    sheet_name = status 
                    write_to_excel(writer, result, sheet_name) 

        elif reportType == 'Buildingwise':  
            building_name = "Building_wise"
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build,selected_floor,selected_station,object_ids,True)
            
            if selected_build:                
                building = Buildings.query.get(selected_build)
                if building:
                    building_name=building.building_name
            result = query.all()        
            write_to_excel(writer, result, building_name) 

        elif reportType == 'Floorwise':  
            floor_name ="Floor_wise"
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build,selected_floor,selected_station,object_ids,True)
            
            if selected_floor:                
                floor = Floors.query.get(selected_floor)
                floor_name = floor.floor_name
               
               
            result = query.all()        
            write_to_excel(writer, result, floor_name)  

        elif reportType == 'Stationwise':  
            station_name="Station_wise"
           
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build,selected_floor,selected_station,object_ids,True)
          
            if selected_station:                
                station = Stations.query.get(selected_station)
                station_name = station.station_name    
               
            result = query.all()        
            write_to_excel(writer, result, station_name) 

        elif reportType == 'Metalexceptionwise':  
            sheet_name = "Metalexceptionwise"
            query = apply_filters(query, fromdate, todate, selected_employees, selected_shifts,selected_transaction,selected_gender,selected_build,selected_floor,selected_station,object_ids)
        
           
            result = query.all()   
            logs = prepare_logs(result)
           
          
            write_to_excel(writer, result, sheet_name) 
    

    file_url = url_for('static', filename=f'reports/{report_name}', _external=True)

    return jsonify({"message": "Report generated successfully", "file_url": file_url, "record_count": len(prepare_logs(result)) if 'logs' in locals() else 0})

def write_to_excel(writer, result, sheet_name):
    if result:
        logs = prepare_logs(result)
        df = pd.DataFrame(logs)
        
        # Add a serial number column
        df.insert(0, 'S.No.', range(1, len(df) + 1))
        
        # Write the DataFrame to the Excel sheet
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        # Auto-fit column widths
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        for i, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2  # Add some padding
            worksheet.set_column(i, i, max_length)
    else:
        # If no records are found, create the sheet and write "No records found"
        worksheet = writer.book.add_worksheet(sheet_name)  # Create the worksheet explicitly
        worksheet.write(0, 0, 'No records found')

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
            'Emp ID': log.employee_number,
            'Employee Name': log.employee_name,
            'Gender': log.employee_gender,
            'Shift': shift_full_name,
            'Type Of Metal Exceptions': ' | '.join(body_parts_output)
        })

    return logs


def get_dates(selected_year):
    selected_year = int(selected_year)   
    from_date = datetime(selected_year, 1, 1)   
    to_date = datetime(selected_year, 12, 31)
    return from_date, to_date

def apply_filters(query, fromdate, todate, selected_employees=None, selected_shifts=None, selected_transaction=None, selected_gender=None, selected_build=None, selected_floor=None, selected_station=None,object_ids=None, is_single_selection=False):
    if fromdate and todate:
        query = query.filter(func.date(Employees_log.log_date_time) >= fromdate,
                             func.date(Employees_log.log_date_time) <= todate)
    
    if selected_employees:
        query = query.filter(Employees_log.employee_number.in_(selected_employees))
     
    if selected_shifts:
        query = query.filter(Employees_log.shift.in_(selected_shifts))

    if selected_transaction:
        query = query.filter(Employees_log.status.in_(selected_transaction)) 

    if selected_gender:
        query = query.filter(Employees.gender.in_(selected_gender))  

    if selected_build:
        if is_single_selection:
            query = query.filter(Employees_log.building == selected_build)  # Single selection
        else:
            query = query.filter(Employees_log.building.in_(selected_build))  # Multiple selections

    if selected_floor:
        if is_single_selection:
            query = query.filter(Employees_log.floor == selected_floor)  # Single selection
        else:
            query = query.filter(Employees_log.floor.in_(selected_floor))  # Multiple selections

    if selected_station:
        if is_single_selection:
            query = query.filter(Employees_log.station == selected_station)  # Single selection
        else:
            query = query.filter(Employees_log.station.in_(selected_station))  # Multiple selections
    if object_ids:
       query = query.filter(
        not_(
            Employees_log.object_ids.in_(object_ids)
        )
    )
  
 
    return query


@reports_bp.route('/building/floor-detail', methods=['POST'])
def get_floors():
    building_ids = request.json.get('building_ids', []) 
    print(f"Received building IDs: {building_ids}") 

    if not building_ids:
        return jsonify({'data': []})  
   
    floors = db.session.query(Floors, Buildings.building_name).\
        join(Buildings, Floors.building_id == Buildings.id).\
        filter(Floors.building_id.in_(building_ids)).\
        all()

    print(f"Floors found: {floors}")
    response_data = [{
        'id': floor.id,
        'floor_name': floor.floor_name,
        'building_id': floor.building_id,
        'building_name': building_name  
    } for floor, building_name in floors]

    return jsonify({'data': response_data})

@reports_bp.route('/building/floor/station-detail', methods=['POST'])
def get_station_details():
    # Get building IDs from the request
    building_ids = request.json.get('building_ids', [])
    floor_ids = request.json.get('floor_ids', [])
    
    if not building_ids and not floor_ids:
        return jsonify({'data': []})
    
    # Build the query to fetch station details along with floor and building names
    query = db.session.query(
        Stations.id.label('station_id'),
        Stations.station_name,
        Floors.floor_name,
        Buildings.building_name
    ).join(Floors, Stations.floor_id == Floors.id).join(Buildings, Floors.building_id == Buildings.id)

    if building_ids:
        query = query.filter(Buildings.id.in_(building_ids))
    if floor_ids:
        query = query.filter(Floors.id.in_(floor_ids))
    
    stations = query.all()

    # Format the response data
    response_data = [{
        'station_id': station_id,
        'station_name': station_name,
        'floor_name': floor_name,
        'building_name': building_name
    } for station_id, station_name, floor_name, building_name in stations]

    return jsonify({'data': response_data})