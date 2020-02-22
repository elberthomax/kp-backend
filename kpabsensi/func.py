from flask import abort
from kpabsensi.models import pegawai, absensi
import face_recognition

def strCheck(string, stringName, stringLen, null=True):
	if type(string) is not str:
		abort(400, stringName + " tidak ada atau bukan string")
	if not null:
		if string == "":
			abort(400, stringName + " tak boleh kosong")
	if len(string) > stringLen:
		abort(400, stringName + " tak boleh lebih dari " + \
		stringLen + " karakter")

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
