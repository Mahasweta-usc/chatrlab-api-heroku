import os, sys
import urllib, requests
import psycopg2
from google.cloud import storage
from flask import Flask, request, session, render_template, redirect, url_for
import urllib.parse, urllib.request, json, pickle 
import pandas as pd
from postgres import *
app = Flask(__name__) 
app.secret_key = "Mahasweta" 

def clean():
	dir_name = os.path.join(os.path.dirname(__file__),"static","images")
	test = os.listdir(dir_name)
	for item in test:
	    if item.endswith(".png"):
	        os.remove(os.path.join(dir_name, item))

def download_blob(source_blob_name, destination_file_name, bucket_name = "procvaxx"):
	storage_client = storage.Client.create_anonymous_client()
	bucket_t = storage_client.bucket("procvaxx", user_project=None)
	temp = storage.Blob(source_blob_name, bucket_t)

	temp.download_to_filename(destination_file_name)

data = pd.read_csv('samples.csv')
file_list = []

for ind in data.index:
	file_list.append(data["filename"][ind])

@app.route('/')
def launch():
	return redirect(url_for('initial'))

@app.route('/login')
def initial():
	initiate()
	return render_template('login.html',warning="")
	

@app.route('/login',methods=['GET','POST'])
def login(): 
	if request.method == 'POST': 
		session['name'] = request.form.get('nm',None).casefold()
		if not session['name']:
			return render_template('login.html',warning="***Please Enter Valid username***")
	try:
		_ = add_column(session["name"])
		return redirect(url_for('update'))
	except Exception as e:
		return redirect(url_for('login'))
	
# @app.route('/about',methods=['GET','POST'])		
# def about():
# 	try:
# 		session["name"]
# 		return render_template('about.html')
# 	except:
# 		return redirect(url_for('initial'))
		
# @app.route('/proceed',methods=['GET','POST'])
# def proceed():
# 	try:
# 		request.form.get('next')
# 		_ = add_column(session["name"])
# 		return redirect(url_for('update'))
# 	except Exception as e:
# 		print(e)
# 		return redirect(url_for('about'))
	
	

@app.route('/input', methods=['GET','POST'])
def update():
	try:
		_ = session["name"]
	except:
		return redirect(url_for('login'))

	
	if 'action' in request.form:

		if request.form.get('action') == "Delete":
			remove(session["file"])

		elif request.form.get('action') == "Submit":
			label = request.form.get('label',None)
			# print(label,type(label))
			if label:
				save(session["file"],session["name"],label)

	clean() #remove images
	
	(session["count"],top) = start(session["name"])
	if not top:
		return redirect(url_for('finish'))
	# print("From main",top)
	(session["file"],caption,image_text) = top[:3]
	image_path = os.path.join("static","images",session["file"].strip("xxx-").replace("json","png"))
	#download image
	download_blob(session["file"].replace(".json",".png"), image_path)

	args = {"name": session['name'],"count": session["count"],"caption": caption,"image_text":image_text,"image": image_path}
	return render_template('labeling_template.html',**args)
	

@app.route('/finish')
def finish():
	return "Annotations Complete. Thank You"



if __name__ == '__main__':
    app.run()