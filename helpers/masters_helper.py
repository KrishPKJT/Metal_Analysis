from model.models import *

def getShiftById(sid):
    if sid=='S1':
        sname = 'Shift 1'
    elif sid=='S2':
        sname = 'Shift 2'
    elif sid=='S3':
        sname = 'Shift 3'
    return sname

def getBuildingNameById(bid):
    building = Buildings.query.get(bid)
    return building.building_name

def getFloorNameById(fid):
    floor = Floors.query.get(fid)
    return floor.floor_name

def getStationNameById(stid):
    station = Stations.query.get(stid)
    return station.station_name

def getBodyPartsById(bid):
    body_parts = Bodyparts.query.get(bid)
    return body_parts.body_parts_name
