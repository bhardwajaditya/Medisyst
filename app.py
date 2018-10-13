import pymongo
from pymongo import MongoClient
from flask import Flask, request,make_response
import hmac, hashlib
import base64
import os
import datetime
import csv
import diagnosisClient
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
if __name__ == '__main__':
    app.run( host=os.environ['IP'], port=os.environ['PORT'] ,debug=True)