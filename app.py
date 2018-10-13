import pymongo
from pymongo import MongoClient
from flask import Flask, request,make_response
import hmac, hashlib
import base64
import os
import datetime
import csv
import diagnosisClient
from googlesearch import search
from commons import json_response

client = MongoClient()
db = client['medisyst']
users = db.users

username = "aditya.1998bhardwaj@gmail.com"
password = "Wd85RaFy76Xrw3QBx"
authUrl = "https://sandbox-authservice.priaid.ch/login"
healthUrl = "https://sandbox-healthservice.priaid.ch"
language = "en-gb"

app = Flask(__name__)
diagnosis = diagnosisClient.DiagnosisClient(username, password, authUrl, language, healthUrl)


@app.route('/')
def index():
    return '<h1>Welcome to Medisyst!</h1>'

@app.route('/symptoms')
def symptom():
    A=[]
    bodylocation= diagnosis.loadSymptoms()
    for i in bodylocation:
        res={
            'Name':i['Name'],
            'ID':i['ID']
        }
        A.append(res)
    return json_response(A)
    
@app.route('/diagnosis')
def diagnose():
    if(request.method=='GET'):
        symptomID = request.args.get('ID')
        gender = request.args.get('gender')
        dob = request.args.get('DOB')
        symptomID=symptomID.split(',')
        info = diagnosis.loadDiagnosis(symptomID,gender,int(dob))
        psymptoms = diagnosis.loadProposedSymptoms(symptomID,gender,int(dob))
        info.append(psymptoms)
        return json_response(info)

@app.route('/bodylocations')
def bodylocations():
    A=[]
    bodylocation = diagnosis.loadBodyLocations()
    for i in bodylocation:
        res={
            'Name':i['Name'],
            'ID':i['ID']
        }
        A.append(res)
    return json_response(A)

@app.route('/sublocations')
def sublocations():
    bodyID=request.args.get('ID')
    gender = request.args.get('Gender')
    slocations = diagnosis.loadSublocationSymptoms(bodyID,int(gender))
    return json_response(slocations)

@app.route('/key')
def generate():
    x=request.args.get('name')
    x=x+str(datetime.datetime.now())
    rawHashString = hmac.new(bytes(x, encoding='utf-8'), x.encode('utf-8')).digest()
    computedHashString = base64.b64encode(rawHashString).decode()
    return computedHashString
    
@app.route('/signup')
def signup():
    email=request.args.get('email')
    password=request.args.get('password')
    aadhaar = request.args.get('aadhaar')
    gender = request.args.get('gender')
    fname = request.args.get('fname')
    lname =request.args.get('lname')
    dob = request.args.get('dob')
    A=[]
    x=users.find({"email":email})
    for i in x:
        A.append(x)
    if(len(A)==0):
        user={
            "email":email,
            "password":password,
            "aadhaar":aadhaar,
            "gender":gender,
            "fname":fname,
            "lname":lname,
            "dob":dob
        }
        x=users.insert_one(user)
        print(x)
        return "yes"
    else:
        return 'no'

@app.route('/login')
def signin():
    email=request.args.get('email')
    password=request.args.get('password')
    A=[]
    x=users.find_one({"email":email})
    print(x)
    if(x['password']==password):
        return "yes"
    else:
        return "no"
        
@app.route('/search')
def gsearch():
    query = request.args.get('query')
    A=[]
    for j in search(query, num=10, stop=1): 
        A.append(j)
    return json_response(A)
    
if __name__ == '__main__':
    app.run( host=os.environ['IP'], port=os.environ['PORT'] ,debug=True)