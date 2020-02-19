from  flask import request, render_template, abort
from kpabsensi.models import pegawai, absensi
import face_recognition
import json, datetime, pytz, calendar, sqlalchemy
import numpy as np
from kpabsensi import app, db
import kpabsensi.func as func

@app.route('/')
def index():
    return "hellow API kp, hhhh -_-"

@app.route('/login', methods=['POST'])
def login():
	parsedJson = request.get_json(force=True)
	if type(parsedJson) is not dict:
		abort(400, "json bukan dictionary")
	func.strCheck(parsedJson.get('id'), "id", 10, False)
	func.strCheck(parsedJson.get('password'), "password", 64, True)
	parsedJson["idNumber"] = parsedJson.pop("id")
	query = func.getPegawai(parsedJson)
	if query is not None:
		return render_template('login.html', param=parsedJson, data=query)
	else:
		return render_template('login.html', param=parsedJson)

@app.route('/absen', methods=['POST'])
def absen():
	try:
		parsedJson=json.loads(request.form.get('json'))
	except:
		abort(400, "invalid json")
	if type(parsedJson) is not dict:
		abort(400, "json bukan dictionary")
	func.strCheck(parsedJson.get('id'), "id", 10, False)
	func.strCheck(parsedJson.get('password'), "password", 64, True)

	queryJson = {"idNumber": parsedJson["id"]}
	found = func.getPegawai(queryJson)
	if found is None:
		return render_template('absen.html',param=parsedJson, \
		errorMsg="id tidak ditemukan")
	parsedJson["idNumber"] = parsedJson.pop("id")
	imgEnc = func.imgToEnc(request.files.get("photo"))
	if type(imgEnc) is str:
		return render_template('absen.html',param=parsedJson, \
		errorMsg=imgEnc)
	knownImg=[np.array(json.loads(found.image1))]
	knownImg.append(np.array(json.loads(found.image2)))
	knownImg.append(np.array(json.loads(found.image3)))
	results = face_recognition.compare_faces(knownImg, imgEnc, tolerance=0.5)
	total = 0
	for result in results:
		total += result
	if total < 2:
		return render_template('absen.html',param=parsedJson, \
		errorMsg="identitas gambar tak sesuai")
	else:
		now = datetime.datetime.utcnow()
		now = pytz.utc.localize(now)
		now = now.astimezone(pytz.timezone('Asia/Makassar'))
		parsedJson['name'] = found.name
		parsedJson['date'] = now.date()
		parsedJson['time'] = now.time()
		parsedJson.pop('password')
		if parsedJson['time'].hour < 12:
			parsedJson['status'] = 'IN'
		else:
			parsedJson['status'] = 'OUT'
		db.session.add(absensi(**parsedJson))
		db.session.commit()
		return render_template('absen.html',param=parsedJson)

@app.route('/getAbsensi', methods=['POST'])
def getAbsensi():
	parsedJson = request.get_json(force=True)
	if type(parsedJson.get('id')) is not str and\
	type(parsedJson.get('bulan')) is not int and\
	type(parsedJson.get('tahun')) is not int:
		abort(400, "id, bulan atau tahun tidak ada atau bertipe salah")
	parsedJson['id'] = parsedJson['id'].strip()
	if parsedJson['id'] == "":
		return render_template("getAbsensi.html", param=parsedJson,\
		errorMsg="id kosong")
	if len(parsedJson['id']) > 10:
		return render_template("getAbsensi.html", param=parsedJson,\
		errorMsg="id terlalu panjang(max 10 karakter)")
	if parsedJson['tahun'] < 1 or parsedJson['tahun'] > 9999:
		return render_template("getAbsensi.html", param=parsedJson,\
		errorMsg="tahun tidak valid(1-9999)")
	if parsedJson['bulan'] < 1 or parsedJson['bulan'] > 12:
		return render_template("getAbsensi.html", param=parsedJson,\
		errorMsg="bulan tidak valid(1-12)")
	data=[]
	for i in range(1, calendar.monthrange(\
	parsedJson['tahun'], parsedJson['bulan'])[1] + 1):
		data.append({"tanggal": i})
	query = absensi.query.filter(\
	sqlalchemy.extract('year', absensi.date) == parsedJson['tahun'], \
	sqlalchemy.extract('month', absensi.date) == parsedJson['bulan'])\
	.filter_by(idNumber = parsedJson['id']).order_by(\
	sqlalchemy.asc(absensi.time)).all()
	for row in query:
		index=row.date.day - 1
		operation=row.status.lower()
		if data[index].get(operation) is None or operation == "out":
			data[index][operation] = {\
			'jam': row.time.hour, \
			'menit': row.time.minute, \
			'detik': row.time.second}
	return render_template("getAbsensi.html", param=parsedJson, \
	data=json.dumps(data))


@app.route('/form')
def form():
    return render_template('imageForm.html')

@app.route('/absenForm')
def absenForm():
    return render_template('absenForm.html')


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
