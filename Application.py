from flask import Flask
import flask
app = Flask(__name__)
from flask import Flask, render_template, request
from flask import request
# from cassandra.cluster import Cluster
import uuid
from werkzeug.utils import secure_filename
import os
from bs4 import BeautifulSoup
import requests
import base64
import cv2
from tabulate import tabulate
import pyttsx3
from pyzbar import pyzbar
import numpy as np


import operator
import json
import time

app = Flask(__name__, static_url_path='')

#cluster = Cluster()
#session = cluster.connect()
#rows = session.execute("create table usr.userDetails (id UUID PRIMARY KEY, emailId text, password text)")
#rows = session.execute("create table usr.userPreference (id UUID, store text, rating float, count int, PRIMARY KEY (id, store))")

	
@app.route('/', methods = ['GET'])
def signin():
	return render_template("login.html")

@app.route('/getAllDetails', methods = ['GET'])
def getAllDetails():
#	rows = session.execute("select id, emailId from usr.userDetails")
	return json.dumps(list(rows))
	# return render_template("login.html")

	
@app.route('/signup', methods = ['POST'], endpoint='signup')
def signup():
	emailId = request.form['emailId']
	password = request.form['password']
#	rows = session.execute("Select id from usr.userDetails where emailId=%s allow filtering", (emailId, ))
#	for row in rows:
#		return render_template("signup.html", message="Email Already Exists")
#	uid = uuid.uuid1()
#	session.execute("insert into usr.userDetails (id, emailId, password) values (%s, %s, %s)", (uid, emailId, password))
	return render_template("login.html", message="You can now log in!")

@app.route('/login', methods = ['POST'], endpoint='login')
def login():
	emailId = request.form['emailId']
	password = request.form['password']
	# rows = session.execute("select id from usr.userDetails where emailId=%s and password=%s allow filtering", (emailId, password))
#	for row in rows:
#		return render_template('barcode.html', id=str(row.id))
	return render_template('scanBarcode.html')
#	return render_template("login.html", message="Invalid EmailId/Password")
	
@app.route('/addPreference', methods = ['GET'])
def addPref():
	id = request.args.get('id')
	store = request.args.get('store')
	rating = request.args.get('rating')
	# id = request.form['id']
	# store = request.form['store']
	# rating = request.form['rating']
	id = uuid.UUID(id)
	rating = float(rating)
#	rows = session.execute("select store, rating, count from usr.userPreference where id=%s and store=%s", (id, store));
#	for row in rows:
#		count = row.count + 1;
#		newRating = (rating + row.rating)/count;
#		session.execute("update usr.userPreference set count=%s and rating=%f where id=%s and store=%s", (count, newRating, id, store));
#		return str(id)
#	rows = session.execute("insert into usr.userPreference (id, store, rating, count) values (%s, %s, %f, %d)", (id, store, rating, 0));
	return str(id)
	
@app.route("/decode", methods=["GET"])
def decode():
	image =  'dummy.png'
	barcodeData = decodeBarcode(image)
	result={}
	if len(barcodeData)==0:
		result['status'] = 'Error'
		print('******************')
		textToSpeech = 'Barcode not found!'
		print(textToSpeech)
		print('******************')
	else:
		productName = getProductName(barcodeData)
		productName = productName.strip('\n')
		if len(productName)==0:
			result['status'] = 'Error'
			print('******************')
			textToSpeech = 'Product not found!'
			print(textToSpeech)
			print('******************')
		else:
			productPrices = getDataAPI(productName)
			
			result['status'] = 'Success'
			result['productName'] = productName

			priceData = sorted(productPrices.items(), key = operator.itemgetter(1))
			result['data'] = priceData

			#result['preference'] = preferenceData

			print('******************')
			textToSpeech = productName
			print(productName)
			print('******************')
			print(tabulate(priceData, headers=['Vendor', 'Price']))

	# os.remove(image)
	# engine = pyttsx3.init()
	# engine.say(textToSpeech)
	# engine.runAndWait()
	if len(result)==0:
		result['status'] = 'Error'
	result = json.dumps(result)
	print(result)
	return result

@app.route('/upload', methods = ['POST'])
def upload():
	imgdata = base64.b64decode(request.form['hidden_data'])
	filename = 'dummy.jpgs'  # I assume you have a way of picking unique filenames
	with open(filename, 'wb') as f:
		f.write(imgdata)
	time.sleep(10)
	priceData = []
	textToSpeech = ''
	result = {}
	image =  'dummy.jpg'
	barcodeData = decodeBarcode(image)
	if len(barcodeData)==0:
		result['status'] = 'Error'
		print('******************')
		textToSpeech = 'Barcode not found!'
		print(textToSpeech)
		print('******************')
	else:
		productName = getProductName(barcodeData)
		productName = productName.strip('\n')
		if len(productName)==0:
			result['status'] = 'Error'
			print('******************')
			textToSpeech = 'Product not found!'
			print(textToSpeech)
			print('******************')
		else:
			productPrices = getDataAPI(productName)
			
			result['status'] = 'Success'
			result['productName'] = productName

			priceData = sorted(productPrices.items(), key = operator.itemgetter(1))
			result['data'] = priceData

			#result['preference'] = preferenceData

			print('******************')
			textToSpeech = productName
			print(productName)
			print('******************')
			print(tabulate(priceData, headers=['Vendor', 'Price']))

	os.remove(image)
	# engine = pyttsx.init()
	# engine.say(textToSpeech)
	# engine.runAndWait()
	if len(result)==0:
		result['status'] = 'Error'
	result = json.dumps(result)
	print(result)
	# os.remove(filename)
	return result
	
def decodeBarcode(imagePath):
	# load the input image
	image = cv2.imread(imagePath)
	barcodeData = ''
	print(image)
	if type(image)==None:
		return barcodeData
	
	# find the barcodes in the image and decode each of the barcodes
	barcodes = pyzbar.decode(image)

	# loop over the detected barcodes
	for barcode in barcodes:
		# extract the bounding box location of the barcode and draw the
		# bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
		 
		# the barcode data is a bytes object so if we want to draw it on
		# our output image we need to convert it to a string first
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type
		 
		# draw the barcode data and barcode type on the image
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	return barcodeData

		

def getDataAPI(productName):
	priceData = {}
	words = productName.split(' ')
	query = ''
	for w in words:
		query += w + '+'
	query = query[:len(query)-1]
		
	url = 'https://www.google.com/search?q=' + query + '&tbm=shop&source=lnms&sa=X&ved=0ahUKEwioxMrrheXgAhUXvZ4KHZSIAEIQ_AUICigB&biw=1211&bih=719&dpr=1'
	  
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	allP = soup.find_all('div', class_='A8OWCb')

	productPrices = {}
	for p in allP:
		p = p.text
			
		dotIdx = p.find('.')
		price = p[:dotIdx+3]
		price = price.replace(',', '')
		price = float(price[1:])
			
		seller = p[dotIdx+3:]
			
		if seller.split(' ')[0].lower() == 'from':
			continue
		else:
			seller = seller.lower()
			hyphenIdx = seller.find('-')
			if hyphenIdx!=-1:
				seller = seller[:hyphenIdx]
				seller = seller.strip()
			if seller in productPrices:
				existingP = productPrices[seller]
				if price<existingP:
					productPrices[seller] = price
			else:
				productPrices[seller] = price

	return productPrices
				

def getProductName(barcodeData):
	url = "https://www.barcodelookup.com/" + barcodeData
		
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	allP = soup.find_all('h4')

	for p in allP:
		p = p.text
		return p
	return ''



app.run(host='0.0.0.0', port=5000)