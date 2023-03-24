#!/usr/bin/env python3

import os
import sys
from flask import Flask, render_template, request, redirect
import importlib

home_directory = os.path.expanduser('~')
template_subfolder = 'Pigrow/webpage/basic_templates'
static_subfolder = 'Pigrow/webpage/basic_static'
handler_subfolder = 'Pigrow/webpage/basic_handler'
port = 8080
template_folder = os.path.join(home_directory, template_subfolder)
static_folder = os.path.join(home_directory, static_subfolder)

for argu in sys.argv:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'index':
            template_folder = theval
        elif thearg == 'static':
            static_folder = theval
        elif thearg == 'handler':
            handler_subfolder = theval
        elif thearg == 'port':
            port = int(theval)
    elif argu == "-h" or "help" in argu:
        print("Host's a webpage on the local network")
        print("")
        print("index= path to the folder containing index.html")
        print("static= path to the folder containing images, etc")
        print("handler= path to folder containing handler.py")
        print("port=8080")
        sys.exit()
    elif argu == "-flags":
        print("index=" + homedir + "/Pigrow/webpage/basic_templates")
        print("static=" + homedir + "/Pigrow/webpage/basic_static")
        print("handler="+ homedir + "/Pigrow/webpage/basic_handler")
        print("port=8080")
        sys.exit()

def import_handler(folder_path):
    handler_file_path = os.path.join(folder_path, 'handler.py')

    if os.path.exists(handler_file_path):
        spec = importlib.util.spec_from_file_location('handler', handler_file_path)
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
        print("handler.py imported")
        return handler
    else:
        print("handler.py not found")
        return None

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json['text']
    response = Handler.call_command(text)
    return response

def main():
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    handler_module = import_handler(handler_subfolder)
    Handler = handler_module.Handler()

    main()
