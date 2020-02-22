from flask import abort
from kpabsensi.models import pegawai, absensi
import face_recognition, calendar, datetime

def strCheck(string, stringName, stringLen, null=True):
	if type(string) is not str:
		abort(400, stringName + " tidak ada atau bukan string")
	if not null:
		if string == "":
			abort(400, stringName + " tak boleh kosong")
	if len(string) > stringLen:
		abort(400, stringName + " tak boleh lebih dari " + \
		stringLen + " karakter")

def intCheck(integer, intName, intMax):
	if type(integer) is not int:
		abort(400, intName + " tidak ada atau bukan integer")
	if integer < 0 or integer > intMax:
		abort(400, intName + " diluar batas(0 - " + str(intMax) + ")")

def dateCheck(year, month, day):
	intCheck(year, "tahun", 9999)
	intCheck(month, "bulan", 12)
	dayRange = calendar.monthrange(year, month)
	intCheck(day, "hari", dayRange[1])
	return datetime.date(year, month, day)
	

def getPegawai(queryJson, booleanOnly = False):
	query = pegawai.query.filter_by(**queryJson).first()
	if booleanOnly:
		return query is not None
	else:
		return query

def imgToEnc(img, postVar):
	if img is None or img.filename == "":
		return "tidak ada gambar pada key" + postVar
	try:
		img = face_recognition.load_image_file(img)
		img = face_recognition.face_encodings(img)
	except:
		return "file pada key " + postVar + " bukan gambar"
	if len(img) == 0:
		return "wajah tak ditemukan pada key " + postVar
	elif len(img) > 1:
		return "lebih dari 1 wajah ditemukan pada key " + postVar
	else:
		return img[0]
