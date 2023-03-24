#!/usr/bin/env python3

import os
import sys
from flask import Flask, render_template, request, redirect
import importlib

homedir = os.getenv("HOME")

def set_folders(main_folder):
    template_folder = os.path.join(main_folder, 'templates')
    static_folder = os.path.join(main_folder, 'static')
    handler_folder = os.path.join(main_folder, 'handler')
    index_file = os.path.join(template_folder, 'index.html')
    if not os.path.isfile(index_file):
        print("File not found:" + index_file)
        exit()
    return template_folder, static_folder, handler_folder

# defaults
port = 8080
autoreload = True
template_folder, static_folder, handler_folder = set_folders(homedir + "/Pigrow/webpage/basic")

for argu in sys.argv:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'index':
            template_folder = theval
        elif thearg == 'folder':
            template_folder, static_folder, handler_folder = set_folders(theval)
        elif thearg == 'static':
            static_folder = theval
        elif thearg == 'handler':
            handler_folder = theval
        elif thearg == 'port':
            port = int(theval)
        elif thearg == "reload":
            if theval.strip().lower() == "true":
                autoreload = True
            else:
                autoreload = False
    elif argu == "-h" or "help" in argu:
        print("Host's a webpage on the local network")
        print("")
        print("folder= path to folder contaning subfolders")
        print("                   templates, static, handler")
        print("index= path to the folder containing index.html")
        print("static= path to the folder containing images, etc")
        print("handler= path to folder containing handler.py")
        print("port=8080")
        print("reload=True  updates hosted page when file changes ")
        sys.exit()
    elif argu == "-flags":
        print("folder=" + homedir + "/Pigrow/webpage/basic")
        print("index=" + homedir + "/Pigrow/webpage/basic/templates")
        print("static=" + homedir + "/Pigrow/webpage/basic/static")
        print("handler="+ homedir + "/Pigrow/webpage/basic/handler")
        print("port=8080")
        print("reload=True")
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
if autoreload:
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    template_files = [os.path.join(template_folder, f) for f in os.listdir(template_folder)]
    static_files = [os.path.join(static_folder, f) for f in os.listdir(static_folder)]
    extra_files = template_files + static_files
else:
    extra_files = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json['text']
    response = Handler.call_command(text)
    return response

def main():

    print("Tracking;" + str(extra_files))
    app.run(host='0.0.0.0', port=port, extra_files=extra_files)

if __name__ == '__main__':

    handler_module = import_handler(handler_folder)
    if not handler_module == None:
        Handler = handler_module.Handler()

    main()
