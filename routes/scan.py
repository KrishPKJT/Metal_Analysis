from flask import Blueprint, render_template,session,redirect,request,jsonify,url_for
from sqlalchemy import text,func, or_
from sqlalchemy.dialects.postgresql import array

from model.models import *
from helpers.masters_helper import *
import re
import random
import string
import pytesseract
import os
from PIL import Image
scan_bp = Blueprint('scan', __name__)

def generate_random_filename(length=10, extension='txt'):
    # Generate random letters and digits
    characters = string.ascii_letters + string.digits
    random_name = ''.join(random.choice(characters) for _ in range(length))
    return f"{random_name}.{extension}"


@scan_bp.route('/get_o_values')
def get_o_values():
    # Define your raw SQL query
    raw_query = text("""
        SELECT EL.* FROM (SELECT
            json_array_elements(objects::json) ->> 'o' AS o_values
        FROM employees_log) AS EL WHERE NOT ('2' = ANY (string_to_array(o_values, ','))) 
    """
    )
    
    # Execute the raw SQL query
    result = db.session.execute(raw_query).mappings()
    
    r = ''
    # Fetch all results
    o_values = [row['o_values'] for row in result]

    return {"o_values": o_values}

@scan_bp.route('/get_o_values1')
def get_o_values1():
   

    subquery = db.session.query(
        Employees_log.log_date_time,
        Employees_log.building,
        func.json_array_elements_text(Employees_log.objects.cast(db.JSON)).label('o_values')
    ).filter(
        Employees_log.building == 2
    ).subquery()

    result = db.session.query(subquery).filter(
        or_(
            ~(func.any(func.string_to_array(subquery.c.o_values, ','))!='2' ),
             func.any(func.string_to_array(subquery.c.o_values, ','))!='4' 
        )
    ).all()
    
    o_values = [row['o_values'] for row in result]

    return {"o_values": o_values}

@scan_bp.route('/scan')
def scan():
    shift_name = getShiftById(session['shift'])
    building_name = getBuildingNameById(session['building'])
    floor_name = getFloorNameById(session['floor'])
    station_name = getStationNameById(session['station'])
    return render_template('scan.html',shift_name=shift_name,building_name=building_name,floor_name=floor_name,station_name=station_name)

@scan_bp.route("/get-log-list",methods=['GET'])
def get_log_list():
    logs_with_employee_info = db.session.query(
        Employees_log,
        Employees.name,
        Employees.gender
    ).join(Employees, Employees.employee_number == Employees_log.employee_number).all()

    results = []
    for log, name, gender in logs_with_employee_info:
        results.append({
            'log_id': log.id,
            'employee_number': log.employee_number,
            'log_date_time': log.log_date_time,
            'employee_name': name,
            'employee_gender': gender
        })

    return jsonify(results)

@scan_bp.route('/saveData',methods=['POST'])
def saveData():
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    Employees.query.filter_by(employee_number=request.form.get('emp_number')).update({"gender":request.form.get('gender'),"medical_implants":request.form.get('medical_implants'),"medical_implants_position":request.form.get("medical_implants_position")})
    db.session.commit()
    newLog = Employees_log(employee_number=request.form.get('emp_number'),points=request.form.get('points'),objects=request.form.get('object'),log_date_time=current_time,status=request.form.get('status'),shift=request.form.get('shift'),building=request.form.get('building'),floor=request.form.get('floor'),station=request.form.get('station'),object_ids=request.form.get('object_ids'),created_by=session['logged_user'])
    db.session.add(newLog)
    db.session.commit()
    return {"status":"ok","msg":"Saved successfully"}


@scan_bp.route('/upload', methods=['POST'])
def upload_image():
    
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image_file = request.files['image']
    if image_file.filename == '':
        return redirect(url_for('index'))
    
    image_file.filename = generate_random_filename(15, 'jpg')
    # Save the uploaded image to a temporary location
    image_path = os.path.join('static/uploads', image_file.filename)
    image_file.save(image_path)
    
    
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    
    print(text)
    match = re.search(r'Employee Number:\s*(\d+)', text)
    gender =""
        
    employee_number = ""
    emp_name = ""
    medical_implants = [];
    medical_implants_position = [];
    if match:
        employee_number = match.group(1)
        ("Employee Number:", employee_number)
        
        if employee_number!="":
            employee = Employees.query.filter_by(employee_number=employee_number).first()

            if employee:
                gender = employee.gender
                emp_name = employee.name
                medical_implants = employee.medical_implants
                medical_implants_position = employee.medical_implants_position
                #if os.path.exists(image_path):
                    #os.remove(image_path)
            else:
                textArr = text.split('\n')
                cleaned_textArr = [item for item in textArr if item.strip()]
                pattern = r'Employee Number'
                index = -1
                for i, item in enumerate(cleaned_textArr):
                    if re.search(pattern, item):  # Use re.search to check for a match
                        index = i
                        break
                if index==0:
                     os.remove(image_path)
                     return {"status":"failed","msg":"Can't read the name from id card"}
                
                if index>=1:
                    nameIdx = index-1
                    emp_name = cleaned_textArr[nameIdx].replace("-","")
                
                gender = request.form.get('gender')
                if os.path.exists(image_path):
                    old_img_path = image_path
                    os.rename(image_path, 'static/uploads/'+employee_number+'.jpg')                    
                newEmployee = Employees(name=emp_name, employee_number=employee_number,gender=gender,image=employee_number+'.jpg',created_by=session['logged_user'])
                db.session.add(newEmployee)
                db.session.commit()
            
            return {"status":"ok","msg":"Processed successfully","emp_number":employee_number,"emp_name":emp_name,"emp_gender":gender,"medical_implants":medical_implants,"medical_implants_position":medical_implants_position}
        
        else:
            return {"status":"failed","msg":"Processed successfully","emp_number":employee_number}
    
    else:
       if os.path.exists(image_path):
        os.remove(image_path)
       return {"status":"failed","msg":"Can't read the id card , scan again"}
   
