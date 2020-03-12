import os, sys
import psycopg2
from google.cloud import storage
from flask import Flask, request, session, render_template, redirect, url_for
import urllib.parse, urllib.request, json, pickle 

# dirname = os.path.dirname(__file__)
app = Flask(__name__) # template_folder='templates')
app.secret_key = "Mahasweta" 

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# image_path = "https://storage.cloud.google.com/procvaxx/"

background = os.path.join(os.path.dirname(__file__),"static","images","background.png")
dir_name = os.path.join(os.path.dirname(__file__),"static","images")
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".png"):
        os.remove(os.path.join(dir_name, item))

def read_json(filename):
	storage_client = storage.Client.create_anonymous_client()
	bucket = storage_client.bucket(bucket_name="labeled_vaxx",user_project=None)	
	blob = bucket.blob(filename)
	data = json.loads(blob.download_as_string(client=None))
	# print(data)
	return data
	
def download_blob(source_blob_name, destination_file_name, bucket_name = "procvaxx"):
	storage_client = storage.Client.create_anonymous_client()
	bucket_t = storage_client.bucket("procvaxx", user_project=None)
	temp = storage.Blob(source_blob_name, bucket_t)

	temp.download_to_filename(destination_file_name)

def write_json(filename,data):
	storage_client = storage.Client.create_anonymous_client()
	bucket = storage_client.bucket(bucket_name="labeled_vaxx",user_project=None)
	blob = bucket.blob(filename)
	data = json.dumps(data)
	blob.upload_from_string(data)

# string = {"Test": 1}
# #print(read_json('record.json'))
@app.route('/')
def launch():
	return redirect(url_for('initial'))

@app.route('/login')
def initial():
	return render_template('login.html',warning="")
	

@app.route('/login',methods=['GET','POST'])
def login(): 
	if request.method == 'POST': 
		session['name'] = request.form.get('nm',None)
		# print(session['name'])
		with open(os.path.join(os.path.dirname(__file__),"static","record.json"),'r') as op:
			users = list(json.load(op)["List"][-1].keys())
		if not session['name']:
			return render_template('login.html',warning="***Please Enter Valid username***")
		elif session["name"] in users:
			return redirect(url_for('form_update'))
		else:
			return redirect(url_for('about'))
# @app.route('/start', methods=['GET','POST'])
# def form_display():
# 	global session['name']
# 	print("session['name']:",session['name'])
# 	remaining = read_json('record.json')['List']
	
@app.route('/about',methods=['GET','POST'])		
def about():
	try:
		session["name"]
		return render_template('about.html')
	except:
		return redirect(url_for('initial'))
		
@app.route('/proceed',methods=['GET','POST'])
def proceed():
	# print(request.form)
	try:
		request.form.get('next')
		return redirect(url_for('form_update'))
	except:
		pass

@app.route('/input', methods=['GET','POST'])
def form_update():
	try:
		session["name"]
	except:
		return redirect(url_for('initial'))

	with open(os.path.join(os.path.dirname(__file__),"static","record.json"),'r') as op:
		remaining = json.load(op)["List"]

	# file = remaining[0]
	# image_path = os.path.join("static","images",file.strip("xxx-").replace("json","png"))

	if 'action' in request.form:

		if request.form.get('action') == "Delete":
			pass

		elif request.form.get('action') == "Skip":
			remaining.insert(len(remaining)-1,session["file"])

		elif request.form.get('action') == "Submit":
			sentiment = request.form.get('senti',None) #,'label']
			label = request.form.get('label',None)

			if label and sentiment:

				contents = read_json(session["file"])

				try:
					test = contents["Annotations"]
				except:
					contents["Annotations"] = {}

				
				contents["Annotations"][session['name']] = {"Stance": sentiment,"Misinformation": label}
				write_json(session["file"],contents)
				remaining[-1][session['name']] = remaining[-1].get(session['name'],0) + 1	


		
		image_path = os.path.join("static","images",session["file"].strip("xxx-").replace("json","png"))
		os.system("rm {}".format(image_path))



	# with open(os.path.join(os.path.dirname(__file__),"static","record.json"),'r') as op:
	# 	remaining = json.load(op)["List"]

	if len(remaining) > 1:
		session["file"] = remaining[0]
		remaining.remove(session["file"])


		updated = dict()
		updated["List"] = remaining
		print(session["file"],remaining)
		# write_json('record.json',updated)
		with open(os.path.join(os.path.dirname(__file__),"static","record.json"),'w') as op:
			json.dump(updated,op)


		image_path = os.path.join("static","images",session["file"].strip("xxx-").replace("json","png"))
		count = str(remaining[-1].get(session['name'],0))
		download_blob(session["file"].strip("xxx-").replace("json","png"),image_path)

		contents = read_json(session["file"])

		try:
			caption = contents["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
		except:
			caption = "NA"
		try:
			image_text = contents['embed_text']
		except:
			image_text = "NA"

		text = "<br/><b align=center>Caption:</b><br/>" + caption + "<br/><br/><b align=center>Image Text:</b><br/>" + image_text
		args = {"name": session['name'],"count": count,"text": text,"image": image_path}
		# "image": urllib.parse.urljoin(image_path,file.strip("xxx-").replace("json","png"))}
	
		return render_template('labeling_template.html',**args)
	else:
		return redirect(url_for('finish'))
	

@app.route('/finish')
def finish():
	return "Annotations Complete. Thank You"



if __name__ == '__main__':
    app.run()