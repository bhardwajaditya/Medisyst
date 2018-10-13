import pymongo
from pymongo import MongoClient
from flask import Flask, request,make_response
import os
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
    return '<h1>Welcome to Tweety!</h1>'

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
        info = diagnosis.loadDiagnosis([13,28],diagnosisClient.Gender.Male,1998)
        return json_response(info)
    
if __name__ == '__main__':
    app.run( host=os.environ['IP'], port=os.environ['PORT'] ,debug=True)