from flask_restful import Resource, reqparse
from flask import Blueprint, request, Response,jsonify
from sqlalchemy.exc import IntegrityError

from hswebapp import app,db

from hswebapp.api import apiv0
from datetime import datetime
from time import sleep

from werkzeug.security import generate_password_hash,check_password_hash
from hswebapp.models.system_models import User,Logs
from hswebapp.models.sensor_models import TempLog,HumidityLog,PressureLog,PowerLog,EventLog
from hswebapp.models.resources import sensorlogs_schema,templog_schema,powerlogs_schema


import copy


@apiv0.route('/apiv1/templogs/<int:lastreadings>', methods=['GET'])
def get_templogs(lastreadings,):

    templog= TempLog.query.order_by(TempLog.rdate.desc()).limit(lastreadings).all()
    result = sensorlogs_schema.dump(templog)
    return jsonify({'templogs': result.data})

@apiv0.route('/apiv1/sensorlog', methods=['GET'])
def get_sensorlogs():
    
    page = request.args.get('page', 1, type=int)
    #sensor = request.args.get('sensor', 'temperature_sensor1',type=string)
     
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    #example:
    #data = User.to_collection_dict(User.query, page, per_page, 'apiv0.get_users')
    return jsonify(data)

@apiv0.route('/templog', methods=['POST'])
def create_register():
    json_data = request.get_json() or {}
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    
    data, errors = templog_schema.load(json_data)    
    
    if errors:
        return jsonify(errors), 422 
    
    new_log = TempLog(**data)
    
    try:
        log = TempLog.query.filter_by(id=new_log.id).first()
        if log:
            return jsonify({"message": "The log already exists","id":log.id}), 400
            
    except Exception as e:
        app.logger.error("Error BD: {} ".format(e))
        db.session.rollback()
        return jsonify({"message": "Error processing your request try again later"}), 503    
    
    finally:
        db.session.close()
        
    
        
    try:         
        db.session.add(new_log)
        db.session.commit()
    
    except Exception as e:
        app.logger.error("Error BD: {} ".format(e))
        db.session.rollback()
        return jsonify({"message": "Error processing your request try again later"}), 503
    
       
    return jsonify({"message": "Created new log.","id": new_log.id}),201
    
