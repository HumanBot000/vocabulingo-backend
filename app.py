import os
from base64 import b64decode
import flask
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from dotenv import load_dotenv
import duolingo
import inspect
import ssl
source = inspect.getsource(duolingo)
new_source = source.replace('jwt=None', 'jwt')
new_source = source.replace('self.jwt = None', ' ')
exec(new_source, duolingo.__dict__)

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/check_credentials',methods=['POST'])
def check_credentials():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:   #User not found does only raise default exception
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.Response("{'success':'True'}", status=200, mimetype='application/json')
if __name__ == '__main__':
    app.run(ssl_context="adhoc",debug=True,port=5000)