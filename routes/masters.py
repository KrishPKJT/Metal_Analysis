from flask import Blueprint, render_template,session,redirect,request,jsonify
from model.models import *
masters_bp = Blueprint('masters', __name__)

@masters_bp.route('/masters')
def masters():
    return render_template('masters.html')

@masters_bp.route('/building/save', methods=['POST'])
def saveBuilding():
    building_id = request.form.get('building_id')
    building_name = request.form.get('building_name')
    if building_id: 
        building = Buildings.query.get(building_id)
        if building:
            building.building_name = building_name
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed'})
    else:  
        newBuilding = Buildings(building_name=building_name, createdAt=get_current_time())
        db.session.add(newBuilding)
        db.session.commit()
        return jsonify({'status': 'ok'})

    
@masters_bp.route('/building/get-list', methods=['POST'])
def getBuildingList():
    draw = request.form.get('draw', type=int) 
    limit = request.form.get('length', default=10, type=int) 
    offset = request.form.get('start', default=0, type=int)   
    total_records = Buildings.query.count()   
    buildings = Buildings.query.offset(offset).limit(limit).all()   
    building_list = [{'id': building.id, 'building_name': building.building_name} for building in buildings]

    buildingData = {
        "draw": draw,                      
        "recordsTotal": total_records,     
        "recordsFiltered": total_records,  
        "data": building_list              
    }

    return jsonify(buildingData)

@masters_bp.route('/building/get/<int:id>', methods=['GET'])
def getBuilding(id):
    building = Buildings.query.get(id)
    if building:
        building_data = {'id': building.id, 'building_name': building.building_name}
        return jsonify({'status': 'ok', 'building': building_data})
    else:
        return jsonify({'status': 'failed'})
    
@masters_bp.route('/building/delete', methods=['POST'])
def deleteBuilding():
    building_id = request.form.get('id')
    
    if building_id:
        building = Buildings.query.get(building_id)
        if building:
            db.session.delete(building)
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed', 'message': 'Building not found'})
    return jsonify({'status': 'failed', 'message': 'Invalid building ID'})

@masters_bp.route('/building/list', methods=['get'])
def getBuildList():
   buildings = Buildings.query.all()   
   building_list = [{'id': building.id, 'building_name': building.building_name} for building in buildings]
   return jsonify({'data': building_list})

@masters_bp.route('/floor/save', methods=['POST'])
def savefloor():
    floor_id = request.form.get('floor_id')
    build_id = request.form.get('build_id')
    floor_name = request.form.get('floor_name')
    if floor_id: 
        floor = Floors.query.get(floor_id)
        if floor:
            floor.floor_name = floor_name
            floor.building_id = build_id
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed'})
    else:  
        newFloor = Floors(floor_name=floor_name,building_id=build_id, createdAt=get_current_time())
        db.session.add(newFloor)
        db.session.commit()
        return jsonify({'status': 'ok'})
    
@masters_bp.route('/floor/get-list', methods=['POST'])
def getFloorTableList():
    draw = request.form.get('draw', type=int) 
    limit = request.form.get('length', default=10, type=int) 
    offset = request.form.get('start', default=0, type=int)   
    total_records = Floors.query.count()   
    floor_data = db.session.query(Floors, Buildings).filter(Floors.building_id == Buildings.id).offset(offset).limit(limit).all()   
    floor_list = [
        {
            'id': floor.id,
            'floor_name': floor.floor_name,
            'building_name': building.building_name,
            'building_id': floor.building_id
        }
        for floor, building in floor_data
    ]

    FloorData = {
        "draw": draw,                      
        "recordsTotal": total_records,     
        "recordsFiltered": total_records,  
        "data": floor_list              
    }

    return jsonify(FloorData)
@masters_bp.route('/floor/get/<int:id>', methods=['GET'])
def getFloor(id):
    floor = Floors.query.get(id)
    if floor:
        floor_data = {'id': floor.id, 'building_id': floor.building_id,'floor_name':floor.floor_name}
        return jsonify({'status': 'ok', 'floor': floor_data})
    else:
        return jsonify({'status': 'failed'})
@masters_bp.route('/floor/delete', methods=['POST'])
def deleteFloor():
    floor_id = request.form.get('id')    
    if floor_id:
        floor = Floors.query.get(floor_id)
        if floor:
            db.session.delete(floor)
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed', 'message': 'Floornot found'})
    return jsonify({'status': 'failed', 'message': 'Invalid Floor ID'})

@masters_bp.route('/floor/list', methods=['POST'])
def get_floor_list():
    building_id = request.form.get('building_id')    
    if not building_id:
        return jsonify([])  
    floors = Floors.query.filter_by(building_id=building_id).all()
    floor_list = [{'id': floor.id, 'floor_name': floor.floor_name} for floor in floors]
    return jsonify(floor_list)

@masters_bp.route('/station/save', methods=['POST'])
def savestation():
    station_id = request.form.get('station_id')
    build_station_id = request.form.get('build_station_id')
    station_name = request.form.get('station_name')
    floor_station_id = request.form.get('floor_station_id')
    if station_id: 
        station = Stations.query.get(station_id)
        if station:
            station.station_name = station_name
            station.building_id = build_station_id
            station.floor_id = floor_station_id
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed'})
    else:  
        newStation = Stations(station_name=station_name,building_id=build_station_id,floor_id=floor_station_id, createdAt=get_current_time())
        db.session.add(newStation)
        db.session.commit()
        return jsonify({'status': 'ok'})
@masters_bp.route('/station/get-list', methods=['POST'])
def getStationTableList():
    draw = request.form.get('draw', type=int) 
    limit = request.form.get('length', default=10, type=int) 
    offset = request.form.get('start', default=0, type=int)   
    total_records = Stations.query.count()  # Get the total number of stations

    # Join Stations with Buildings and Floors using their respective IDs
    station_data = db.session.query(Stations, Buildings, Floors)\
        .filter(Stations.building_id == Buildings.id)\
        .filter(Stations.floor_id == Floors.id)\
        .offset(offset)\
        .limit(limit)\
        .all()

    # Create a list of stations with building and floor details
    station_list = [
        {
            'id': station.id,
            'station_name': station.station_name,
            'building_name': building.building_name,
            'floor_name': floor.floor_name,
            'building_id': station.building_id,
            'floor_id': station.floor_id
        }
        for station, building, floor in station_data
    ]

    StationData = {
        "draw": draw,                      
        "recordsTotal": total_records,     
        "recordsFiltered": total_records,  
        "data": station_list
    }

    return jsonify(StationData)

    
@masters_bp.route('/station/get/<int:id>', methods=['GET'])
def getStation(id):
    station = Stations.query.get(id)
    if station:
        staion_data = {'id': station.id, 'building_id': station.building_id,'station_name':station.station_name,'floor_id':station.floor_id}
        return jsonify({'status': 'ok', 'station': staion_data})
    else:
        return jsonify({'status': 'failed'})
@masters_bp.route('/station/delete', methods=['POST'])
def deleteStation():
    station_id = request.form.get('id')    
    if station_id:
        station = Stations.query.get(station_id)
        if station:
            db.session.delete(station)
            db.session.commit()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'failed', 'message': 'Station not found'})
    return jsonify({'status': 'failed', 'message': 'Invalid Station ID'})
    
@masters_bp.route('/station/list', methods=['POST'])
def get_station_list():
    building_id = request.form.get('building_id')
    floor_id = request.form.get('floor_id')    
    if not building_id:
        return jsonify([])    
    
    if floor_id:
        station = Stations.query.filter_by(building_id=building_id, floor_id=floor_id).all()
    else:
        station = Stations.query.filter_by(building_id=building_id).all()

    
    station_list = [{'id': stations.id, 'building_id': stations.building_id,'station_name':stations.station_name,'floor_id':stations.floor_id} for stations in station]

    return jsonify(station_list)