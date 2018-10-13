import pymongo
from pymongo import MongoClient
from flask import Flask, request,make_response,render_template, url_for, request,redirect
import hmac, hashlib
import base64
import os
import datetime
import csv
import diagnosisClient
from googlesearch import search
from commons import json_response
from bson.objectid import ObjectId


client = MongoClient()
db = client['medisyst']
users = db.users
doctors=db.doctors
addrequests=db.addrequests

username = "aditya.1998bhardwaj@gmail.com"
password = "Wd85RaFy76Xrw3QBx"
authUrl = "https://sandbox-authservice.priaid.ch/login"
healthUrl = "https://sandbox-healthservice.priaid.ch"
language = "en-gb"

app = Flask(__name__)
diagnosis = diagnosisClient.DiagnosisClient(username, password, authUrl, language, healthUrl)


@app.route('/')
def index():
    return render_template('index.html')

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
    
@app.route('/diagnose')
def diagnosepage():
    return render_template('diagnosis.html')
    
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


        
@app.route('/signin',methods = ['POST', 'GET'])
def login():
    if(request.method=='GET'):
        error=""
        return render_template('login.html',error=error)
    if(request.method=="POST"):
        email=request.form['email']
        password=request.form['password']
        A=[]
        doc=doctors.find_one({"email":email})
        print(doc)
        if(doc!=None):
            if(doc['password']==password):
                url='/home/'+str(doc['_id'])
                return redirect(url)
            else:
                error="Password Incorrect"
                return render_template('login.html',error=error)
        else:
            return render_template('signup.html')
            
@app.route('/register',methods = ['POST', 'GET'])
def register():
    if(request.method=="GET"):
        return render_template('signup.html')
    if(request.method=="POST"):
        fname=request.form['fname']
        lname=request.form['lname']
        docid=request.form['docid']
        email=request.form['email']
        password=request.form['password']
        A=[]
        doc=doctors.find({'email':email})
        for i in doc:
            A.append(i)
        if(len(A)==0):
            doctor={
                'fname':fname,
                'lname':lname,
                'docid':docid,
                'email':email,
                'password':password,
                'patients':"None"
            }
            doc=doctors.insert(doctor)
            doc=doctors.find_one({"email":email})
            print(doc)
            url='/home/'+str(doc['_id'])
            return redirect(url)
        else:
            return redirect("/signin")
    
@app.route('/home/<ID>')
def home(ID):
    doc=doctors.find_one({'_id':ObjectId(ID)})
    print(doc['patients'])
    url="/home/"+str(doc['_id'])
    addurl=url+"/add"
    return render_template('home.html',doc=doc,addurl=addurl)

@app.route('/home/<ID>/addkey')
def addkey(ID):
    if(request.method=="POST"):
        name=request.form['name']
        email=request.form['email']
        used="No"
        permission="No"
        x = name+str(datetime.datetime.now())
        rawHashString = hmac.new(bytes(x, encoding='utf-8'), x.encode('utf-8')).digest()
        key = base64.b64encode(rawHashString).decode()
        req={
            'name':name,
            'docid':ID,
            'email':email,
            'used':used,
            'permission':permission,
            'key':key
        }
        y=addrequests.insert_one(req)
        url="/home/"+ID
        return redirect(url)

        
@app.route('/home/<ID>/add')
def add(ID):
    if(request.method=="GET"):
        error=""
        url="/home/"+ID
        return render_template("add.html",error=error,url=url)
    if(request.method=="POST"):
        url="/home/"+ID
        key=request.form['key']
        result = addrequests.find_one({'key':key})
        if(result['used']=="Yes" or result['permission']=="No"):
            error="Key not valid"
            
            return render_template('add.html',error=error,url=url)
        else:
            x=addrequests.update_one({'key':key},{'$set':{'used':"Yes"}})
            print(x)
            patient=users.find_one({'email':result['email']})
            doc=doctors.find_one({'_id':ObjectId(ID)})
            if(doc['patients']=="None"):
                A=[patient]
            else:
                A=doc['patients']
                A.append(patient)
            doc1=doctors.update_one({'_id':ObjectId(ID)},{'$set':{'patients':A}})
            return render_template('addrecord.html',email=result['email'])
        


@app.route('/key')
def generate():
    email=request.args.get('email')
    req = addrequests.find({'email':email})
    A=[]
    for i in req:
        A.append({'name':i['Name'],'ID':i['docid']})
    return json_response(A)
    
    
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