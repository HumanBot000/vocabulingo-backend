import flask

app = flask.Flask(__name__)

@app.route('/check_credentials',methods=['POST'])
def check_credentials():
    password = flask.request.json.get('password')
    email = flask.request.json.get('email')
    
if __name__ == '__main__':
    app.run()