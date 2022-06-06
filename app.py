import os
from flask import Flask

app = Flask(__name__, static_folder = "assets")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True} 
env='okay'
if env='dev':
    app.config['SQLALCHEMY_DATABASE_URI']=''
    app.debug = True

else:
    app.config['SQLALCHEMY_DATABASE_URI']=''
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


from routes import *
from models import *


db.create_all() 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)