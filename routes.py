from flask import request, render_template, abort
from app import app, db
from app.models import pegawai
import face_recognition
import json

@app.route('/login', methods=['POST'])
def login():
	req = request.get_json(force=True)
	if type(req) is not dict:
		abort(400, "json bukan dictionary")
	idNum = req.get('id')
	passw = req.get('password')
	if type(idNum) is not str or type(passw) is not str:
		abort(400, "id atau password kosong atau bukan string")
	if len(idNum) > 10 or len(passw) > 64:
		abort(400, "id atau password terlalu panjang(id max 10 ch,password max 64 ch)")
	found = pegawai.query.filter_by(idNumber=idNum, password=passw).first()
	if found is not None:
		return render_template('login.html', idNumber=idNum, privilege=found.privilege)
	else:
		return render_template('login.html', idNumber=idNum)

@app.route('/form')
def form():
    return render_template('imageForm.html')

@app.route('/input', methods=['POST'])
def input():
	file1 = request.files.get('photo1')
	if file1 is None or file1.filename == "":
		abort(400, "no image")
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

@app.route('/newEmployee', methods=['POST'])
def newEmployee():
	if request.form.get('json') is None or request.form.get('json')  == "":
		abort(400, "no json")
	try:
		jsonParsed = json.loads(request.form.get('json'))
	except:
		abort(400,"invalid json")
	imgs =[request.files.get("image1"), request.files.get("image2"), request.files.get("image3")]
	for img in imgs:
		if(img is None or img.filename == ""):
			abort(400, "gambar tidak lengkap")
	newId=jsonParsed.get('newId')
	newName=jsonParsed.get('newName')
	newPass=jsonParsed.get('newPassword')

	if type(newId) is str and type(newName) is str and type(newPass) is str:
		newId=newId.strip();
		if newId == "":
			return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="Id tidak boleh kosong")
		if len(newId)>10:
			return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="id tidak boleh lebih dari 10 karakter")
		if len(newName)>100:
			return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="nama tidak boleh lebih dari 100 karakter")
		if len(newPass)>64:
			return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="password tidak boleh lebih dari 64 karakter")

	else:
		abort(400, "id, nama atau password tak ada atau bukan string")
	found = pegawai.query.filter_by(idNumber=newId).first()
	if found is not None:
		return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="id sudah ada")
	picEnc=[]
	try:
		for img in imgs:
			pic=face_recognition.load_image_file(img)
			picEnc.append(face_recognition.face_encodings(pic)[0])
	except:
		return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="file bukan gambar atau muka tak ditemukan")
	results = face_recognition.compare_faces([picEnc[1], picEnc[2]], picEnc[0], tolerance=0.5)
	if not(results[0] and results[1]):
		return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="identitas gambar tak saling bersesuaian")
	results = face_recognition.compare_faces([picEnc[2]], picEnc[1], tolerance=0.5)
	if not(results[0]):
		return render_template('newEmployee.html', newId=newId, newName=newName, newPassword=newPass, errorMsg="identitas gambar tak saling bersesuaian")
	toAdd = pegawai(idNumber=newId, name=newName, password=newPass,image1=json.dumps(picEnc[0].tolist()), image2=json.dumps(picEnc[1].tolist()), image3=json.dumps(picEnc[2].tolist()))
	db.session.add(toAdd)
	db.session.commit()
	return render_template('newEmployee.html', newId=newId, newName=newName,newPassword=newPass)
