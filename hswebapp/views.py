from flask import Blueprint,render_template,flash, redirect, url_for, request, Response,Flask,jsonify
from jinja2 import TemplateNotFound
from hswebapp import app,db,login_manager,model_saved
from hswebapp.models.sensor_models import TempLog,HumidityLog,PressureLog,PowerLog,EventLog
from hswebapp.models.resources import sensorlog_schema,powerlog_schema
from datetime import datetime
#from sqlalchemy.exc import IntegrityError
from flask_login import login_required,login_user,logout_user, current_user
from hswebapp.models.system_models import User

views = Blueprint('views', __name__,template_folder='templates')


def add_event(message):
    return message
   
    
@views.route('/')
def home():
    return render_template('pages/home.html')


@views.route("/environment")
@login_required
def dashboard():
    import sys
    
    try:                       
        temperature_sensor1= TempLog.query.order_by(TempLog.rdate.desc()).filter_by(sensorType='AM2302').first()          
        temperature_sensor2= TempLog.query.order_by(TempLog.rdate.desc()).filter_by(sensorType='DH11').first()                        
        temperature_sensor3= TempLog.query.order_by(TempLog.rdate.desc()).filter_by(sensorType='BMP180').first()
                      
        humidity_sensor1= HumidityLog.query.order_by(HumidityLog.rdate.desc()).filter_by(sensorType='AM2302').first()     
        humidity_sensor2= HumidityLog.query.order_by(HumidityLog.rdate.desc()).filter_by(sensorType='DH11').first()        
                        
        pressure_sensor1= PressureLog.query.order_by(PressureLog.rdate.desc()).first()
            
        power_sensor1 =   PowerLog.query.order_by(PowerLog.rdate.desc()).first()                     
                       
    except:
        flash("InvalidRequestError: {} ".format(sys.exc_info()[0]))
        
        raise
        db.session.rollback()
        return redirect(url_for('home'))
    finally:
        db.session.close()
    
    if (temperature_sensor2 is None):
        return 'no data'
    
    return render_template("pages/dashboard.html",temperature_sensor1=temperature_sensor1,
                                temperature_sensor2=temperature_sensor2,
                                temperature_sensor3=temperature_sensor3,
                                humidity_sensor1=humidity_sensor1,
                                humidity_sensor2=humidity_sensor2,
                                pressure_sensor1=pressure_sensor1,
                                power_sensor1=power_sensor1,
                                TempLog=TempLog,
                                HumidityLog=HumidityLog,
                                PressureLog=PressureLog,
                                PowerLog=PowerLog
                                )
  
        
@views.route('/readings', methods=["GET"])
@login_required
def report_listreadings():
    try:
        temperature = TempLog.query.order_by(TempLog.rdate.desc()).limit(50).all()
        humidity = HumidityLog.query.order_by(HumidityLog.rdate.desc()).limit(50).all()
        pressure = PressureLog.query.order_by(PressureLog.rdate.desc()).limit(50).all()
        power = PowerLog.query.order_by(PowerLog.rdate.desc()).limit(50).all()
    
    except:
        flash("InvalidRequestError: {} ".format(sys.exc_info()[0]))
        
        raise
        db.session.rollback()
        return redirect(url_for('home'))
    finally:
        db.session.close()
        
   
    return render_template("readings.html", temperature = temperature,humidity =humidity, pressure = pressure, power = power)
               

@views.route('/grafics', methods=["GET"])
def report_grafics():
    

    try:
           
                            
            result=TempLog.query.count()
            templog= TempLog.query.order_by(TempLog.rdate.desc()).limit(10).all()
            humiditylog= HumidityLog.query.order_by(HumidityLog.rdate.desc()).limit(10).all()
            pressurelog= PressureLog.query.order_by(PressureLog.rdate.desc()).limit(10).all()
            powerlog =   PowerLog.query.order_by(PowerLog.rdate.desc()).limit(10).all()
        
        
    except:
        app.logger.error("InvalidRequestError: {} ".format(sys.exc_info()[0]))
        
        raise
        db.session.rollback()
        return redirect(url_for('home'))
    finally:
        db.session.close()
        
        
    return render_template("pages/grafics.html",ntemp=result,
                                temp = templog,
                                humididylog= humiditylog,
                                pressurelog=pressurelog,
                                powerlog=powerlog
                                )
    
         
   
    
@views.route('/about1', methods=["GET"])
@login_required
def about1():
    return render_template("pages/about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"),404

    
@model_saved.connect
def model_saved_signal(app, message, **extra):
#check what page/template is beind rendered
    
    try:
        event=EventLog(ob_id=message.get_id(), ob_type=message.get_type())
        event.save_to_db()
    
    except Exception as e:
        app.logger.error('Update error: {}'.format(e))
        db.session.rollback()
    
    finally:
        db.session.close()
    
 
@views.route('/update_dashboard', methods=['POST'])
@login_required
def update_dashboard():
      
    page_load=(request.form['page_load']) 
    
    fmt="YYYY-mm-ddTHH:MM:SS.SSSZ"
    py_format='YYYY-MM-DDTHH:MM:SS'    
    jsdate=datetime.strptime(page_load, '%Y-%m-%dT%H:%M:%S.%fZ')
        
    #ValueError: time data '2017-12-17T20:46:23.438Z' does not match format 'YYYY-MM-DDTHH:MM:SS'
    #datetime_object = datetime.strptime(page_load,py_format)
    #print('##############date###################')
    #print(jsdate)
    #print('##############date###################')        
    #now_utc = datetime.now(timezone('UTC'))
    
    try:
        if  (EventLog.query.count()==0) :
            return jsonify({'result' : 'no_data','last_Attempt': datetime.now()})
        else: 
            event = EventLog.query.order_by(EventLog.id.asc()).first()
        
        
    except:
        app.logger.error("InvalidRequestError: {} ".format(sys.exc_info()[0]))
        
        raise
        db.session.rollback()
        return jsonify({'result' : 'no_data','last_Attempt': datetime.now()})
    
            
    if (event.ob_type=='TempLog'):
        updated=TempLog.query.filter_by(id=event.ob_id).first()
      
    elif (event.ob_type=='HumidityLog'):
        updated=HumidityLog.query.filter_by(id=event.ob_id).first()   
    elif (event.ob_type=='PressureLog'):
        updated=PressureLog.query.filter_by(id=event.ob_id).first()   
    elif (event.ob_type=='PowerLog'):
        updated=PowerLog.query.filter_by(id=event.ob_id).first() 
    
    event.delete_from_db()  

    if (type(updated) is PowerLog):
        result = powerlog_schema.dump(updated)
        return powerlog_schema.jsonify(updated)
    else :
        result = sensorlog_schema.dump(updated)
        #pprint(result)
        return sensorlog_schema.jsonify(updated)
        

@views.route('/update_event', methods=['POST'])
@login_required
def dashboard_event():
    pass    
# retreive the the time that the page has been loaded and return the next event_id to be refreshed


@app.shell_context_processor
def make_shell_context():
    return{'db':db,'User':User, 'Templog':TempLog}    
    
@views.route('/update_templog', methods=['POST'])
def update_templog():
    data = request.get_json() or {}
    
    return jsonify({"message": "temperature value {} ".format(data.value)}), 201
    