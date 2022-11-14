import json
import flask
import os

app = flask.Flask(__name__)
schedule_fn = 'schedule.txt'


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/edit-schedule')
def sched():
    dat = '{}'
    if os.path.exists(schedule_fn):
        with open(schedule_fn, 'r') as f:
            dat = json.loads(f.read())
    return flask.render_template('schedule.html', schedule=dat)


@app.route('/edit-schedule', methods=['POST'])
def update_sched():
    new_schedule = flask.request.get_json()
    with open(schedule_fn, 'w') as f:
        f.write(json.dumps(new_schedule))
    return flask.redirect(flask.url_for('sched'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
