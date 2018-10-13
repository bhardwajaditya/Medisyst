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

# addrequests.insert_one({
#         "permission": "Yes",
#         "used": "No",
#         "name": "Aditya Bhardwaj",
#         "key": "abcd",
#         "email":"Aditya@gmail.com"
        
#     })

# users.delete_many({})
# doctors.delete_many({})
# addrequests.delete_many({})

x=users.find()
for i in x:
    print(i)

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
        print(symptomID)
        symptomID=symptomID.split(',')
        info = diagnosis.loadDiagnosis(symptomID,gender,int(dob))
        
        s=""
        B=[]
        for i in info:
            for j in i['Specialisation']:
                s = s+','+j['Name'] 
            doc={
                'name':i['Issue']['Name'],
                'specialisation':s[1:],
                'profname':i['Issue']['ProfName'],
                'accuracy':i['Issue']['Accuracy']
            }
            B.append(doc)
        return json_response(B)


        
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

@app.route('/home/<ID>/addkey',methods = ['POST', 'GET'])
def addkey(ID):
    if(request.method=="POST"):
        name=request.form['Name']
        email=request.form['email']
        used="No"
        permission="No"
        x = name+str(datetime.datetime.now())
        rawHashString = hmac.new(bytes(x, encoding='utf-8'), x.encode('utf-8')).digest()
        key = base64.b64encode(rawHashString).decode()
        req={
            'name':name,
            'email':email,
            'used':used,
            'permission':permission,
            'key':key
        }
        y=addrequests.insert_one(req)
        url="/home/"+ID
        return redirect(url)

        
@app.route('/home/<ID>/add',methods = ['POST', 'GET'])
def add(ID):
    if(request.method=="GET"):
        error=""
        url="/home/"+ID
        addkey=url+"/addkey"
        return render_template("add.html",error=error,url=url,addkey=addkey)
    if(request.method=="POST"):
        url="/home/"+ID
        key=request.form['key']
        result = addrequests.find_one({'key':key})
        print(result['email'])
        if(result['used']=="Yes" or result['permission']=="No"):
            error="Key not valid"
            
            return render_template('add.html',error=error,url=url)
        else:
            x=addrequests.update_one({'key':key},{'$set':{'used':"Yes"}})
            print(x)
            patient=users.find_one({'email':result['email']})
            doc=doctors.find_one({'_id':ObjectId(ID)})
            print(doc)
            print(patient)
            if(doc['patients']=="None"):
                A=[patient]
            else:
                A=doc['patients']
                A.append(patient)
            doc1=doctors.update_one({'_id':ObjectId(ID)},{'$set':{'patients':A}})
            return render_template('addrecord.html',patient=patient,url=url)
        
@app.route('/history',methods = ['POST', 'GET'])
def history():
    if(request.method=="GET"):
        email=request.args.get('email')
        user=users.find_one({'email':email})
        return json_response(user['history'])
    if(request.method=="POST"):
        name=request.form['name']
        date=request.form['date']
        email=request.form['email']
        docname=request.form['docname']
        profname=request.form['profname']
        treatment=request.form['treatment']
        ID=request.form['ID']
        doc={
            'name':name,
            'date':date,
            'profname':profname,
            'docname':docname,
            'treatment':treatment
        }
        user=users.find_one({'email':email})
        if(user['history']=="None"):
            A=[doc]
        else:
            A=user['history']
            A.append(doc)
            user1=user.update_one({'email':email},{'$set':{'history':A}})
            url="/home/"+ID
            return redirect(url)
    

@app.route('/key')
def generate():
    email=request.args.get('email')
    req = addrequests.find({})
    A=[]
    for i in req:
        print(i)
        A.append({'name':i['name'],'key':i['key'],'permission':i['permission'],'used':i['used']})
    return json_response(A)
    
@app.route('/allow')
def allow():
    key=request.args.get('key')
    addrequests.update_one({'key':key},{'$set':{'allowed':'Yes'}})
    return "Yes"
    
@app.route('/tempsignup')
def signup():
    email=request.args.get('email')
    password=request.args.get('password')
    # aadhaar = request.args.get('aadhaar')
    # gender = request.args.get('gender')
    # fname = request.args.get('fname')
    # lname =request.args.get('lname')
    # dob = request.args.get('dob')
    A=[]
    user={
        "email":email,
        "password":password,
        "history":"None"
        }
    x=users.insert_one(user)
    print(x)
    return "1"
    

@app.route('/login')
def signin():
    email=request.args.get('email')
    password=request.args.get('password')
    A=[]
    x=users.find_one({"email":email})
    print(x)
    if(x['password']==password):
        return "1"
    else:
        return "0"

@app.route('/update')
def update1():
    email=request.args.get('email')
    aadhaar = request.args.get('aadhaar')
    gender = request.args.get('gender')
    fname = request.args.get('fname')
    lname =request.args.get('lname')
    dob = request.args.get('dob')
    x=users.update_one({'email':email},{'$set':{gender:gender,aadhaar:aadhaar,fname:fname,lname:lname,dob:dob}})
    return "1"

@app.route('/check')
def check():
    email=request.args.get('email')
    x=users.find({'email':email})
    A=[]
    for i in x:
        A.append(i)
    if(len(A)==0):
        return "0"
    else:
        return "1"
    
@app.route('/search')
def gsearch():
    query = request.args.get('query')
    A=[]
    for j in search(query, num=10, stop=1): 
        A.append(j)
    return json_response(A)
    
if __name__ == '__main__':
    app.run( host=os.environ['IP'], port=os.environ['PORT'] ,debug=True)