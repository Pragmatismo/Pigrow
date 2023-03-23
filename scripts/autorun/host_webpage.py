#!/usr/bin/env python3

import os
import sys
from flask import Flask, render_template, request, redirect

home_directory = os.path.expanduser('~')
template_subfolder = 'Pigrow/webpage/basic_templates'
static_subfolder = 'Pigrow/webpage/basic_static'
handler = None
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
            handler = theval
        elif thearg == 'port':
            port = int(theval)
    elif argu == "-h" or "help" in argu:
        print("Host's a webpage on the local network")
        print("")
        print("index= path to the folder containing index.html")
        print("static= path to the folder containing images, etc")
        print("port=8080")
        sys.exit()
    elif argu == "-flags":
        print("index=" + homedir + "/Pigrow/webpage/basic_templates")
        print("static=" + homedir + "/Pigrow/webpage/basic_static")
        #print("handler=" + homedir + "/Pigow/webpage/handler")
        print("port=8080")
        sys.exit()



app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    print("User input:", user_input)
    return redirect('/')

def main():
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
