#!/usr/bin/python
import flask
from flask import request, jsonify
from flask import current_app
from flask_cors import CORS
import sys
import os
import csv
import subprocess
import json
import datetime
from dateutil import parser
from pathlib import Path
import glob
import re

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = False
app.clients = {}

app.config["HOME_PATH"] = r'/home/pi/Pigrow'
home_path  = r'/home/pi/Pigrow'
# default return
@app.route('/', methods=['GET'])
def home():
    return "<h1>Pigrow Mobile API</h1><p>This site is a prototype API for Pigrow monitoring.</p>"

def RunSubprocess(args):
    process = subprocess.run(args,
                         stdout=subprocess.PIPE,
                         universal_newlines=True)
    return process

# A route to return all of the configured triggers.
@app.route('/api/v1/triggers/getalltriggers/<local>', methods=['GET'])
@app.route('/api/v1/triggers/getalltriggers', defaults={'local': None}, methods=['GET'])
def api_GetCurrentTriggers(local):

    results = []
    with open(os.path.join(home_path, 'config/trigger_events.txt')) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader: # each row is a list
            results.append(row)

    triggers = []
    for line in results:
        trigg = {}
        trigg["log"] = line[0]
        trigg["valuelabel"] = line[1]
        trigg["type"] = line[2]
        trigg["value"] = line[3]
        trigg["conditionname"] = line[4]
        trigg["set"] = line[5]
        trigg["lock"] = line[6]
        trigg["cmd"] = line[7]
        triggers.append(trigg)
    if local:
        return triggers
    else:
        return jsonify(triggers)


# get spcific trigger by condition name
@app.route('/api/v1/triggers/gettrigger/<conditionname>', methods=['GET'])
def api_GetTrigger(conditionname):

    results = []
    with open(os.path.join(home_path, 'config/trigger_events.txt')) as csvfile:
        reader = csv.reader(csvfile) # change contents to floats
        for row in reader: # each row is a list
            results.append(row)

    for line in results:
        if line[4].lower() == conditionname.lower():
            trigg = {}
            trigg["log"] = line[0]
            trigg["valuelabel"] = line[1]
            trigg["type"] = line[2]
            trigg["value"] = line[3]
            trigg["conditionname"] = line[4]
            trigg["set"] = line[5]
            trigg["lock"] = line[6]
            trigg["cmd"] = line[7]
            break


    return jsonify(trigg)

# Set trigger value, update exisiting or create new
# resultsJson['createnew'] decide which
@app.route('/api/v1/triggers/settrigger', methods=['POST'])
def api_SetTrigger():
    resultsJson = request.get_json()
    log = resultsJson['log']
    valueLabel = resultsJson['valuelabel']
    typeVal = resultsJson['type']
    value = resultsJson['value']
    conditionname = resultsJson['conditionname']
    setVal = resultsJson['set']
    lock = resultsJson['lock']
    cmd = resultsJson['cmd']
    createNew = resultsJson['createnew']
    success = True
    results = []
    if createNew:
        try:
            with open(os.path.join(home_path, 'config/trigger_events.txt'), 'a+') as file_object:
                file_object.seek(0)
                data = file_object.read(100)
                if len(data) > 0 :
                    file_object.write(",".join(map(str, [log,valueLabel,typeVal,value,conditionname,setVal,lock,cmd])) + '\n')
        except (Exception) as e:
            success = false
    else:
        with open(os.path.join(home_path, 'config/trigger_events.txt')) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                results.append(row)
        with open(os.path.join(home_path, 'config/trigger_events.txt'), 'w') as outf:
            try:
                for line in results:
                    if len(line) > 0:
                        if line[4] == conditionname:
                            outf.write(",".join(map(str, [log,valueLabel,typeVal,value,conditionname,setVal,lock,cmd]))+ '\n')
                        else:
                            outf.write(",".join(map(str, line)) + '\n')
                outf.close()
            except (Exception) as e:
                success = False
                for line in results:
                    outf.write(",".join(map(str, line)) + '\n')
                outf.close()
                #raise InvalidUsage('Write failed', status_code=410)

    return jsonify(str(success))


# Get sensor details
@app.route('/api/v1/config/getallsensors/<local>',  methods=['GET'])
@app.route('/api/v1/config/getallsensors',defaults={'local': None}, methods=['GET'])
def api_GetCurrentSensors(local):
    sensorsFull = {}
    with open(os.path.join(home_path, 'config/pigrow_config.txt')) as f:
        lines = f.read().splitlines()
        for line in lines:
            if line.startswith('sensor_'):
                linetuple = line.split('_')
                if linetuple[1] not in sensorsFull:
                    sensorsFull[linetuple[1].lower()] = {linetuple[2].split('=')[0]:line.split('=')[1]}
                else:
                    sensorsFull[linetuple[1]][linetuple[2].split('=')[0]] =  line.split('=')[1]

    if local:
        return sensorsFull
    else:
        return jsonify(sensorsFull)


# Get specific sensor details by name
@app.route('/api/v1/config/readsensor/<sensorname>/<typeSensor>', methods=['GET'])
@app.route('/api/v1/config/readsensor/<sensorname>', defaults={'typeSensor': 'modular'}, methods=['GET'])
def api_ReadSensor(sensorname,typeSensor='modular'):
    sensors = api_GetCurrentSensors(True)
    sensorSplit = '\n'
    module_path = ''
    if sensorname in sensors:
        sensor = sensors[sensorname]
        sensorScript = Path(home_path + "/scripts/gui/sensor_modules/sensor_" + sensor['type'] + ".py")
        if sensor['type'] and sensorScript.is_file():
            module_path = [home_path + "/scripts/gui/sensor_modules/sensor_" + sensor['type'] + ".py", "location=" + sensor['loc'] ,"name=" + sensorname]
    if typeSensor.lower() == 'chirp':
        sensorScript = Path(home_path + "/scripts/sensors/log_" + sensor['type'] + ".py")
        if sensor['type'] and sensorScript.is_file():
            module_path = [home_path + "/scripts/sensors/log_" + sensor['type'] + ".py", "address=" + sensor['loc'].split(":")[1]]
        sensorSplit = '>'
        if sensor["extra"]:
            minmax = sensor['extra'].split(" ")
            min = minmax[0].split(":")[1]
            max = minmax[1].split(":")[1]
            module_path.append("min=" + min)
            module_path.append("max=" + max )
    if module_path:
        reading = RunSubprocess(module_path)
        line = reading.stdout.strip()
        line = line.replace('Written; ' ,'')
        obj,error = ParseReading(line, typeSensor, None, sensorSplit)
        obj["sensortype"] = sensorname
    else:
        obj = {}
        obj["sensortype"] = sensorname
    #objNamed = {sensorname: obj}

    return jsonify(obj)


# Get and parse config file
@app.route('/api/v1/config/getconfig', methods=['GET'])
def api_GetConfig():
    sensorsFull = {}
    config = {}
    with open(os.path.join(home_path, 'config/pigrow_config.txt')) as f:
        lines = f.read().splitlines()

        for line in lines:
            if line.startswith('sensor_'):
                linetuple = line.split('_')
                if linetuple[1] not in sensorsFull:
                    sensorsFull[linetuple[1]] = {linetuple[2].split('=')[0]:line.split('=')[1]}
                else:
                    sensorsFull[linetuple[1]][linetuple[2].split('=')[0]] =  line.split('=')[1]
            else:
                if line.startswith('gpio'):
                    linetuple = line.split('_',1)
                    if linetuple[0] not in config:
                        config[linetuple[0]] = {linetuple[1].split('=')[0]:line.split('=')[1]}
                    else:
                        config[linetuple[0]][linetuple[1].split('=')[0]] =  line.split('=')[1]
    config['sensors'] = sensorsFull

    return jsonify(config)

# Get gpio details
@app.route('/api/v1/config/getgpio', methods=['GET'])
def api_GetGpio():
    gpioFull = {}
    with open(os.path.join(home_path, 'config/pigrow_config.txt')) as f:
        lines = f.read().splitlines()

        for line in lines:
            if line.startswith('gpio'):
                linetuple = line.split('_',1)
                if linetuple[0] not in gpioFull:
                    gpioFull[linetuple[0]] = {linetuple[1].split('=')[0]:line.split('=')[1]}
                else:
                    gpioFull[linetuple[0]][linetuple[1].split('=')[0]] =  line.split('=')[1]

    return jsonify(gpioFull)

# set gpio toggle
@app.route('/api/v1/config/setgpio/', methods=['POST'])
def api_SetGpio():
    data = request.get_json()
    relayName = data['relayName']
    direction = data['direction']
    pin = data['pin']
    pin = int(pin)
    state = data['state']
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    gpioPowerState = direction
    args = ['echo', str(pin) + '>' + '/sys/class/gpio/export']
    out = RunSubprocess(args)
    args = ['cat', '/sys/class/gpio/gpio' + str(pin) + '/value']
    out = RunSubprocess(args)
    gpio_status = out.stdout.strip()
    gpio_err = ''
    if out.stderr is not None:
        gpio_err = out.stderr.strip()
    success = True
    if gpio_status == "1":
        if gpioPowerState == 'low':
            device_status = "OFF"
        elif gpioPowerState == 'high':
            device_status = 'ON'
        else:
            device_status = "settings error"
            success = False
    elif gpio_status == '0':
        if gpioPowerState == 'low':
            device_status = "ON"
        elif gpioPowerState == 'high':
            device_status = 'OFF'
        else:
            device_status = "setting error"
            success = False
    else:
        device_status = "read error -" + gpio_status + "-"
    if success:
        GPIO.setup(pin, GPIO.OUT)
        if device_status == "OFF" or direction.upper() == "OFF":
            if gpioPowerState == "low":
                GPIO.output(pin, GPIO.LOW)
            elif gpioPowerState == "high":
                GPIO.output(pin, GPIO.HIGH)
        elif device_status == "ON" or direction.upper() == "ON":
            if gpioPowerState == "low":
                GPIO.output(pin, GPIO.HIGH)
            elif gpioPowerState == "high":
                GPIO.output(pin, GPIO.LOW)

    return success

# Check gpio state
@app.route('/api/v1/config/checkgpio/', methods=['POST'])
def api_CheckGpio():
    gpios = request.get_json()
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for gp in gpios:
        if 'direction' in gp:
            gpio = gp['pin']
            gpioPowerState = gp['direction']
            args = ['echo', str(gpio) + '>' + '/sys/class/gpio/export']
            out = RunSubprocess(args)
            args = ['cat', '/sys/class/gpio/gpio' + str(gpio) + '/value']
            out = RunSubprocess(args)
            gpio_status = out.stdout.strip()
            gpio_err = ''
            if out.stderr is not None:
                gpio_err = out.stderr.strip()
            success = True
            if gpio_status == "1":
                if gpioPowerState == 'low':
                    device_status = "OFF"
                elif gpioPowerState == 'high':
                    device_status = 'ON'
                else:
                    device_status = "settings error"
                    success = False
            elif gpio_status == '0':
                if gpioPowerState == 'low':
                    device_status = "ON"
                elif gpioPowerState == 'high':
                    device_status = 'OFF'
                else:
                    device_status = "setting error"
                    success = False
            else:
                device_status = "read error -" + gpio_status + "-"
            gp['state'] = device_status

    return jsonify(gpios)

# get log by logname
@app.route('/api/v1/data/getlog/<logname>', defaults={'logtype': None}, methods=['GET'])
@app.route('/api/v1/data/getlog/<logname>/<logtype>', methods=['GET'])
def api_GetLog(logname,logtype='modular'):

    sensorsText = api_GetCurrentSensors(True)

    if logname.lower() in sensors:
        sensor = sensors[logname]
        logPath = sensor['log']

    logResults,error = ParseLog(logPath,logtype)
    if len(logResults) == 0:
        logResults.append({'error':error})
    return jsonify(logResults)


# get log by name and specififc fields
# post json object contaings contents of logConfig below
@app.route('/api/v1/data/getcustomlog/', methods=['POST'])
def api_GetCustomLog():
    logConfig = request.get_json()
    logPath = logConfig['log']
    logName = logConfig['name']
    logColumn = logConfig['col']
    logType = logConfig['type']
    options = {}
    options['logPath'] = logPath
    options['logName'] = logName
    options['logColumn'] = logColumn
    options['logType'] = logType

    if 'datestart' in logConfig:
        startDate = logConfig['datestart']
        options['datestart'] = startDate
    if 'dateend' in logConfig:
        endDate = logConfig['dateend']
        options['dateend'] = endDate

    logResults,error = ParseLog(logPath,logType,options)
    if len(logResults) == 0:
        logResults.append({'error':error})
    return jsonify(logResults)


# Parse log
def ParseLog(logPath, typeSensor, options=None):

    logsResults = []
    with open(logPath) as f:
        lines = f.read().splitlines()
        error = ""
        for line in lines:
            obj,error = ParseReading(line, typeSensor, options)
            if obj != {}:
                logsResults.append(obj)

    return logsResults,error

# parse log line (supports modular and chirp)
def ParseReading(line, typeSensor, options=None, lineSplit = '>'):
    linePart = line.split(lineSplit)
    obj = {}
    error = ''
    if typeSensor is not None and typeSensor.upper() == 'CHIRP':
        if options:
            dt = linePart[0]
            if 'datestart' in options:
                start = datetime.datetime.strptime(options['datestart'], "%a, %d %b %Y %H:%M:%S %Z")
                end = datetime.datetime.strptime(options['dateend'], "%a, %d %b %Y %H:%M:%S %Z")
                lineDate = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
                if lineDate < start or lineDate > end:
                    return obj,error
            try:
                obj['time'] = dt
            except IndexError:
                error = 'noIndex'
            if 'moisture' in options['logColumn'] or not options['logColumn']:
                try:
                    obj['moisture'] = linePart[1]
                except IndexError:
                    error = 'noIndex'
            if 'moistureperc' in options['logColumn'] or not options['logColumn']:
                try:
                    obj['moistureperc'] = linePart[2]
                except IndexError:
                    error = 'noIndex'
            if 'temperature' in options['logColumn'] or not options['logColumn']:
                try:
                    obj['temperature'] = linePart[3]
                except IndexError:
                    error = 'noIndex'
            if 'light' in options['logColumn'] or not options['logColumn']:
                try:
                    obj['light'] = linePart[4]
                except IndexError:
                    error = 'noIndex'
        else:
            try:
                obj['time'] = linePart[0]
            except IndexError:
                error = 'noIndex'
            try:
                obj['moisture'] = linePart[1]
            except IndexError:
                error = 'noIndex'
            try:
                obj['moistureperc'] = linePart[2]
            except IndexError:
                error = 'noIndex'
            try:
                obj['temperature'] = linePart[3]
            except IndexError:
                error = 'noIndex'
            try:
                obj['light'] = linePart[4]
            except IndexError:
                error = 'noIndex'
    elif not options:
        for part in linePart:
            try:
                split = part.split('=')
                obj[split[0]] = split[1]
            except:
                error = 'incorrect type maybe, default is modular'
    else:
        for part in linePart:
            try:
                split = part.split('=')
                if 'datestart' in options:
                    if split[0] == 'time':
                        start = datetime.datetime.strptime(options['datestart'], "%a, %d %b %Y %H:%M:%S %Z")
                        end = datetime.datetime.strptime(options['dateend'], "%a, %d %b %Y %H:%M:%S %Z")
                        lineDate = datetime.datetime.strptime(split[1], '%Y-%m-%d %H:%M:%S.%f')
                        if lineDate < start or lineDate > end:
                            return obj,error
                        else:
                            obj[split[0]] = split[1]
                    if split[0] in options['logColumn'] or not options['logColumn']:
                        obj[split[0]] = split[1]
                else:
                    if split[0] in options['logColumn'] or options['logColumn'] == {} or split[0] == 'time':
                        obj[split[0]] = split[1]


            except:
                error = 'incorrect type maybe, default is modular'

    return obj,error

# Get all .py files in folder
@app.route('/api/v1/config/getfolderlisting/<folderPath>/<filePrefix>/<fileType>', defaults={'local': None},  methods=['GET'])
def api_GetFolderListing(folderPath, filePrefix, fileType, local):
    try:
        listingObj = []
        folderPath = folderPath.replace('-_','/')
        listings = glob.glob(os.path.join(home_path +  folderPath,"*." + fileType))
        if listings:
            for l in listings:
                listing = {}
                fileName = os.path.basename(l)
                fileName = str(fileName).replace(filePrefix,'').replace('.'+ fileType,'')
                fileName = re.sub('^[^A-Za-z]*', '', fileName)
                listing['name'] = fileName.replace('_',' ')
                listing['id'] = fileName
                listing['relPath'] = str(l).replace(home_path,'').replace('/','-_')
                listingObj.append(listing)
        if local:
            return listingObj
        else:
            return jsonify(listingObj)
    except (Exception) as e:
        return jsonify(e)

# Get simple file response
@app.route('/api/v1/config/getinfo/<relPath>',  methods=['GET'])
def api_GetInfo(relPath):
    response = ''
    try:
        folderPath = relPath.replace('-_','/')
        filePath = os.path.join(home_path +  folderPath)
        if '/gui/info_modules' in folderPath:
            info = RunSubprocess(filePath)
            response = info.stdout
            if not response:
                response = 'No results'
        else:
            response = 'Not Valid!'
        return response
    except (Exception) as e:
        return jsonify(e)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# avail able on local lan only
app.run(host= '0.0.0.0')
