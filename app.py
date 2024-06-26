import json
import flask
import duolingo
import inspect
from gevent import pywsgi
import requests

source = inspect.getsource(duolingo)
new_source = source.replace('jwt=None', 'jwt')
new_source = source.replace('self.jwt = None', ' ')
exec(new_source, duolingo.__dict__)

# todo add an defaul account and use set_username() so no pw or jwt has to be provided
app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


@app.route('/test')
def hello_world():
    return 'Hello, World!'


def jsonify_compact(*args, **kwargs):
    response = flask.jsonify(*args, **kwargs)
    response.data = response.get_data(as_text=True).replace('\n', '').replace("\\", "")
    return response


@app.route('/get_ui_language', methods=['POST'])
def get_ui_language():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return user.get_user_info()['ui_language']


@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except requests.exceptions.ConnectTimeout:
        return flask.Response("{'success':'False'}", status=408, mimetype='application/json')
    except Exception as e:  # User not found does only raise default exception
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.Response("{'success':'True'}", status=200, mimetype='application/json')


@app.route("/get_language_abbreviations", methods=['POST'])
def get_languages():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception as e:
        print(e)
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return jsonify_compact(user.get_languages(abbreviations=True))


@app.route("/get_language_name", methods=['POST'])
def get_language_names():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return user.get_language_from_abbr(lang)


@app.route("/get_full_language_info", methods=['POST'])
def get_language_info():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return [user.get_languages(abbreviations=True), user.get_languages(abbreviations=False)]


@app.route("/get_known_topics", methods=['POST'])
def get_known_topics():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return sorted(user.get_known_topics(lang))


@app.route("/get_vocabularies", methods=['POST'])
def get_vocabulary():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
        vocabs = json.dumps(user.get_vocabulary(lang, user.get_user_info()['ui_language']))
        return flask.Response(str(vocabs), status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
@app.route("/get_user_info", methods=['POST'])
def get_user_info():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.jsonify(user.get_user_info())
@app.route("/get_daily_xp", methods=['POST'])
def daily_xp():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.jsonify(user.get_daily_xp_progress())
if __name__ == '__main__':
    #app.run(ssl_context=('server.crt', 'server.key'), debug=True, port=5000, host="0.0.0.0")   #Normal Operations
    app.run(debug=True, port=5000, host="0.0.0.0",ssl_context="adhoc") #Uncomment for developing mode
