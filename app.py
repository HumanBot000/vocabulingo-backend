import flask
import duolingo
import inspect
source = inspect.getsource(duolingo)
new_source = source.replace('jwt=None', 'jwt')
new_source = source.replace('self.jwt = None', ' ')
exec(new_source, duolingo.__dict__)

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def jsonify_compact(*args, **kwargs):
    response = flask.jsonify(*args, **kwargs)
    response.data = response.get_data(as_text=True).replace('\n', '').replace("\\","")
    return response

@app.route('/check_credentials',methods=['POST'])
def check_credentials():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:   #User not found does only raise default exception
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.Response("{'success':'True'}", status=200, mimetype='application/json')

@app.route("/get_language_abbreviations",methods=['POST'])
def get_languages():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception as e:
        print(e)
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return jsonify_compact(user.get_languages(abbreviations=True))
@app.route("/get_language_name",methods=['POST'])
def get_language_names():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return user.get_language_from_abbr(lang)
@app.route("/get_full_öanguage_info",methods=['POST'])
def get_language_info():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return [user.get_languages(abbreviations=True),user.get_language_from_abbr(lang)]
if __name__ == '__main__':
    app.run(ssl_context="adhoc",debug=True,port=5000)
