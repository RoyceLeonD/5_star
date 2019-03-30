#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import docs
from services import *

#Setting un the Flask framework to process requests

app= Flask(__name__, static_url_path='/static')

#This function refreshes the page, and renders the index.html
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/', methods=["POST"])
def index_post():
    prod_ID_ASINS = request.form['text']
    ReadAsin(AddAsins(prod_ID_ASINS))
    concat()
    #stakeholder_ratings().main_stakeholder_bucketing()
    if prod_ID_ASINS:
        return render_template('loader.html')

@app.route("/data_file")
def data_file():
    return "<a href=%s>file</a>" % url_for('static', filename='data_file.json')

@app.route('/send')
def send():
    return "<a href=%s>file</a>" % url_for('static', filename='demo_data.json')

@app.route("/concat_data_gcnlg")
def concat_data_gcnlg():
    return "<a href=%s>file</a>" % url_for('static', filename='concat_data_gcnlg.json')

@app.route("/concat_data")
def concat_data():
    return "<a href=%s>file</a>" % url_for('static', filename='concat_data.json')

@app.route("/ratings_data")
def ratings_data():
    return send_from_directory('static', '/static/ratings.json')