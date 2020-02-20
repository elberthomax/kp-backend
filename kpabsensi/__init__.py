from flask import Flask
from kpabsensi.config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from kpabsensi import routes, models
if __name__ == "__main__":
    app.run()
#app.run()
