from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()


def get_current_time():
    utc_now = datetime.utcnow()
    local_tz = pytz.timezone('Asia/Kolkata')
    local_time = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_time

# Define a model
class Employees(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    employee_number = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    medical_implants = db.Column(db.String(5000))
    medical_implants_position = db.Column(db.String(5000))
    created_by = db.Column(db.BigInteger)    
    def __repr__(self):
        return f'<Employees {self.id}>'

class Employees_log(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    employee_number = db.Column(db.String(120), nullable=False)
    points = db.Column(db.String(200000),nullable=False)
    objects = db.Column(db.String(200000),nullable=False)
    log_date_time = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(5),nullable=False)
    shift = db.Column(db.String(500),nullable=False)
    building = db.Column(db.BigInteger,nullable=False)
    floor = db.Column(db.SmallInteger,nullable=False)
    station = db.Column(db.SmallInteger,nullable=False)
    object_ids = db.Column(db.String(2000))
    created_by = db.Column(db.BigInteger)
    def __repr__(self):
        return f'<Employees_log {self.id}>'
    
class Users(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250),nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(15), nullable=False)
    rights = db.Column(db.String(2000), nullable=False)
    status = db.Column(db.String(15), nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)
    lastLogin = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Users {self.id}>'

class Buildings(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    building_name = db.Column(db.String(250), nullable=False)  
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)     
    def __repr__(self):
        return f'<Buildings {self.id}>'
    
class Floors(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    floor_name = db.Column(db.String(250), nullable=False)  
    building_id=db.Column(db.BigInteger)
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)     
    def __repr__(self):
        return f'<Floors {self.id}>'
class Stations(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    station_name = db.Column(db.String(250), nullable=False)  
    building_id=db.Column(db.BigInteger)
    floor_id=db.Column(db.BigInteger)
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)     
    def __repr__(self):
        return f'<Stations {self.id}>'

        
class Bodyparts(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    body_parts_name = db.Column(db.String(250), nullable=False)  
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)     
    def __repr__(self):
        return f'<Bodyparts {self.id}>'

class Objectmappings(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    object_name = db.Column(db.String(250), nullable=False)  
    gender = db.Column(db.String(250), nullable=False) 
    body_part_id = db.Column(db.BigInteger) 
    createdAt = db.Column(db.DateTime, nullable=False,default=get_current_time)     
    def __repr__(self):
        return f'<Objectmappings {self.id}>'
