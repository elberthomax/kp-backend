from flask import request
from flask import render_template
from app import app
from app.models import pegawai
import face_recognition

@app.route('/login', methods=['POST'])
def login():
	idNum = request.form.get('id')
	passw = request.form.get('password')
	found = pegawai.query.filter_by(idNumber=idNum, password=passw).first()
	if found is not None:
		return render_template('login.html', idNumber=idNum, privilege=found.privilege)
	else:
		return render_template('login.html', idNumber=idNum)

@app.route('/form')
def form():
    return render_template('loginForm.html')

@app.route('/input', methods=['POST'])
def input():
    file1 = request.files['photo1']
    pic1 = face_recognition.load_image_file(file1)
    pic1Enc = face_recognition.face_encodings(pic1)[0]
    
    file2 = request.files['photo2']
    pic2 = face_recognition.load_image_file(file2)
    pic2Enc = face_recognition.face_encodings(pic2)[0]

    results = face_recognition.compare_faces([pic1Enc], pic2Enc)

    if results[0] == True:
        return "It's the same person"
    else:
        return "not same person"

    #return "name:" + filename1 + " " + filename2 + '\n'

