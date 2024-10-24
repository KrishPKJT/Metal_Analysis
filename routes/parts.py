from flask import Blueprint, render_template,session,redirect,request,jsonify
from model.models import *
from helpers.masters_helper import *
parts_bp = Blueprint('parts', __name__)


@parts_bp.route('/parts')
def parts():
    return render_template('bodyparts.html')

@parts_bp.route('/bodyparts/save', methods=['POST'])
def savebodyparts():
    body_parts_name = request.form.get('body_parts_name')  
    newBodyparts = Bodyparts(body_parts_name=body_parts_name, createdAt=get_current_time())
    db.session.add(newBodyparts)
    db.session.commit()
    return jsonify({'status': 'ok'})

    
@parts_bp.route('/bodyparts/getbody-partlist', methods=['POST'])
def getbodypartList():
    draw = request.form.get('draw', type=int) 
    limit = request.form.get('length', default=10, type=int) 
    offset = request.form.get('start', default=0, type=int)   
    total_records = Bodyparts.query.count()   
    bodyparts = Bodyparts.query.offset(offset).limit(limit).all()     
    body_part_list = [{'body_parts_name': bodypart.body_parts_name} for bodypart in bodyparts]

    bodypartData = {
        "draw": draw,                      
        "recordsTotal": total_records,     
        "recordsFiltered": total_records,  
        "data": body_part_list              
    }

    return jsonify(bodypartData)

@parts_bp.route('/bodyparts/list', methods=['get'])
def getBodyList():
   body = Bodyparts.query.all()   
   body_part_list = [{'body_parts_name': bodypart.body_parts_name,'id':bodypart.id} for bodypart in body]
   return jsonify({'data': body_part_list})

@parts_bp.route('/object/save', methods=['POST'])
def save_object():
    object_id = request.form.get('id')  # Get the object ID if provided
    object_name = request.form.get('object_name')
    gender = request.form.get('gender') 
    body_parts_name = request.form.get('body_parts_name')   
    
    if object_id:  # If ID exists, update the existing object
        existing_object = Objectmappings.query.get(object_id)
        if existing_object:
            existing_object.object_name = object_name
            existing_object.gender = gender
            existing_object.body_part_id = body_parts_name
            existing_object.updatedAt = get_current_time()  # Add updated time if needed
            db.session.commit()
            return jsonify({'status': 'ok', 'message': 'Object updated successfully!'})
        else:
            return jsonify({'status': 'failed', 'message': 'Object not found!'})
    else:  # If no ID, create a new object
        newObject = Objectmappings(object_name=object_name, gender=gender, body_part_id=body_parts_name, createdAt=get_current_time())
        db.session.add(newObject)
        db.session.commit()
        return jsonify({'status': 'ok', 'message': 'Object saved successfully!'})


@parts_bp.route('/object/getobject-list', methods=['POST'])
def getObjectmappingList():
    draw = request.form.get('draw', type=int) 
    limit = request.form.get('length', default=10, type=int) 
    offset = request.form.get('start', default=0, type=int)   
    total_records = Objectmappings.query.count()      
    object = db.session.query(Objectmappings, Bodyparts).filter(Objectmappings.body_part_id == Bodyparts.id).offset(offset).limit(limit).all()   
 
    object_list = [{'id':objectmap.id,'object_name': objectmap.object_name,'gender': objectmap.gender,'body_parts_name': bodypart.body_parts_name} for objectmap,bodypart in object]

    objectData = {
        "draw": draw,                      
        "recordsTotal": total_records,     
        "recordsFiltered": total_records,  
        "data": object_list              
    }

    return jsonify(objectData)

@parts_bp.route('/object/get-list', methods=['get'])
def getObjectList():
   object = Objectmappings.query.all()   
   object_list = [{'id':objectmap.id,'object_name': objectmap.object_name,'gender': objectmap.gender,'body_part_id': objectmap.body_part_id} for objectmap in object]
   return jsonify({'data': object_list})


@parts_bp.route('/object/getgender-object-list', methods=['POST'])
def gender_objects():
    body_part = request.form.get('body_part')
    gender = request.form.get('gender')
    
    body_part = Bodyparts.query.filter_by(body_parts_name=body_part).first()
    if not body_part:
        return jsonify({'error': "'"+request.form.get('body_part')+"' not found"})
    query = Objectmappings.query.filter_by(body_part_id=body_part.id)
   
    if gender == 'male':
        query = query.filter(
            (Objectmappings.gender == 'male') | (Objectmappings.gender == 'male,female')
        )
    elif gender == 'female':
        query = query.filter(
            (Objectmappings.gender == 'female') | (Objectmappings.gender == 'male,female')
        )
    
    object_list = query.all()

    response = [
        {
            'body_parts_name': body_part.body_parts_name,
            'gender': obj.gender,
            'body_part_id': obj.body_part_id,
            'obj_id': obj.id,
            'object_name': obj.object_name
        }
        for obj in object_list
    ]
    ol = Objectmappings.query.get(1)
    response.append({
        'body_parts_name': body_part.body_parts_name,
        'gender': ol.gender,
        'body_part_id': body_part.id,
        'obj_id': ol.id,
        'object_name': ol.object_name
    })
    
    return jsonify(response)

@parts_bp.route('/bodyparts/object/get/<int:id>', methods=['GET'])
def getObject(id):
    Objectmap = Objectmappings.query.get(id)
    if Objectmap:
        object_data = {'id': Objectmap.id, 'object_name': Objectmap.object_name,'gender':Objectmap.gender,'body_part_id':Objectmap.body_part_id}
        return jsonify({'status': 'ok', 'object_data': object_data})
    else:
        return jsonify({'status': 'failed'})
@parts_bp.route('/object/delete/<int:id>', methods=['DELETE'])
def delete_object(id):
    object_to_delete = Objectmappings.query.get(id)
    if object_to_delete:
        db.session.delete(object_to_delete)
        db.session.commit()
        return jsonify({'status': 'ok', 'message': 'Object deleted successfully!'})
    else:
        return jsonify({'status': 'failed', 'message': 'Object not found!'})