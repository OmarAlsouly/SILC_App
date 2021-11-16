import os
from flask import Flask, render_template, request, redirect, session, send_file
from datetime import datetime
from MainFunc import create_dataset

app = Flask(__name__)
app.secret_key = os.urandom(16) #secret key for sessions


#home page route
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        searchterm = request.form["searchterm"]
        create_dataset(searchterm)
        
        return render_template('home.html', search_term=searchterm)

    return render_template('home.html')


@app.route('/download/')
def download():
    file_names = []
    dir_path = 'outputs'
    for filename in sorted(os.listdir(dir_path)):
        if filename.endswith('csv'):
            file_names.append([filename,datetime.strptime(filename.replace('.csv', ''),"%d-%m-%Y-%H-%M")])

    file_names = sorted(file_names, key=lambda x: x[1], reverse=True)


    return render_template('download.html', file_names=file_names)

@app.route('/download/<filename>')
def downloadFile(filename):
#load all of the available csv files, sorting by newer. and add a download button
    path = 'outputs/'+filename
    return send_file(path, as_attachment=True)


    
