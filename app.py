from flask import Flask, render_template, request
import pass_train
import json
app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def page():
    return render_template('index.html')

@app.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = pass_train.list_sessions()
    return json.dumps(sessions)

@app.route('/session', methods=['POST'])
def create_session():
    session = pass_train.create_session()
    pass_train.save_session(session)
    return str(session.id)

@app.route('/next/<sessionid>', methods=['GET'])
def get_next_comparison(sessionid=None):
    sessionid = int(sessionid)
    if sessionid <= 0:
        raise InvalidUsage('Session could not be found', status_code=404)
    session = pass_train.get_session(sessionid)
    result = pass_train.get_next_comparison(session)
    if isinstance(result, pass_train.Comparison):
        comparison = result
        password1 = filter(lambda p: p.id == comparison.id_a, session.passwords)[0].password
        password2 = filter(lambda p: p.id == comparison.id_b, session.passwords)[0].password
        payload = {
            "password1":  password1,
            "password2":  password2,
        }
    elif isinstance(result, list):
        final_list = result
        payload = {
            "final_list": final_list,
        }
    return json.dumps(payload)

@app.route('/next', methods=['POST'])
def post_new_comparison():
    request_body = request.get_json()
    # print request_body
    data = request_body
    # data = json.loads(request_body)
    session = pass_train.get_session(int(data["sessionId"]))
    comparison = pass_train.create_comparison(session, data['password1'], data['password2'], data['result'])
    if pass_train.validate_next_comparison(session, comparison):
        session.comparisons.append(comparison)
        pass_train.save_session(session)
        return json.dumps(True)
    else:
        raise InvalidUsage('Comparison invalid', )

app.run(debug=True)
