import json
import re
import flask
import duolingo
import inspect
from gevent import pywsgi
import requests

# Patch the Duolingo module source code
source = inspect.getsource(duolingo)
new_source = source.replace('jwt=None', 'jwt')
new_source = new_source.replace('self.jwt = None', ' ')
exec(new_source, duolingo.__dict__)

app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route('/test')
def hello_world():
    return 'Hello, World!'

def find_related_words(word, skills):
    found_skills = []
    all_words = set()
    for skill in skills:
        if word in skill["words"]:
            found_skills.append(skill["title"])
            all_words.update(skill["words"])
    return found_skills, all_words

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
    except Exception as e:
        print(e)
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return jsonify_compact({'ui_language': user.get_user_info()['ui_language']})

@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except requests.exceptions.ConnectTimeout:
        return flask.Response("{'success':'False'}", status=408, mimetype='application/json')
    except Exception as e:
        print(e)
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
    return jsonify_compact(user.get_language_from_abbr(lang))

@app.route("/get_full_language_info", methods=['POST'])
def get_language_info():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return jsonify_compact([user.get_languages(abbreviations=True), user.get_languages(abbreviations=False)])

@app.route("/get_known_topics", methods=['POST'])
def get_known_topics():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
    except Exception:
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return jsonify_compact(sorted(user.get_known_topics(lang)))

@app.route("/get_vocabularies", methods=['POST'])
def get_vocabulary():
    jwt = flask.request.json.get('jwt')
    username = flask.request.json.get('user')
    lang = flask.request.json.get('lang')
    try:
        user = duolingo.Duolingo(username=username, jwt=jwt)
        vocabs = user.get_vocabulary(lang, user.get_user_info()['ui_language'])
        skills = user.get_learned_skills(lang)
        for vocab in vocabs:
            related_skills, related_words_set = find_related_words(vocab["text"], skills)
            if related_skills:
                vocab["related_skills"] = related_skills
                vocab["related_words"] = list(related_words_set)
    except Exception as e:
        print(e)
        return flask.Response("{'success':'False'}", status=401, mimetype='application/json')
    return flask.Response(json.dumps(vocabs), status=200, mimetype='application/json')

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
    app.run(debug=True, port=5000, host="0.0.0.0", ssl_context="adhoc")
