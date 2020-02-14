from app import db

class pegawai(db.Model):
	idNumber = db.Column("ID Number", db.String(10), primary_key=True)
	departmentName = db.Column("Department Name", db.String(50))
	name = db.Column("Name", db.String(50), nullable=False)
	password = db.Column(db.String(64),default="")
	card = db.Column("Card", db.Integer,default=0)
	group = db.Column("Group", db.String(10), default="Group1")
	privilege = db.Column("Previlege", db.String(), default="User")
	image1 = db.Column(db.String(1600))
	image2 = db.Column(db.String(1600))
	image3 = db.Column(db.String(1600))

class absensi(db.Model):
	date = db.Column("Date", db.Date, primary_key=True)
	idNumber = db.Column("IDNumber", db.Integer, db.ForeignKey("pegawai.ID Number"), primary_key=True)
	name = db.Column("Name", db.String(50))
	time = db.Column("Time", db.Time, primary_key=True)
	status = db.Column("Status", db.String(5), default="IN")
	verification = db.Column("Verification", db.String(10), default="Password")
