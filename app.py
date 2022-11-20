import flask
import json
import logging
import os
import queue
import threading

import common
import schedule_keeper as sk

app = flask.Flask(__name__)
q = queue.Queue()
log_level logging.ERROR

def main():
    common.init_logging(log_level=log_level, log_fn='server-interface.log')

    t = threading.Thread(target=offline_logic)
    t.start()

    app.run(debug=False, host='0.0.0.0')


def offline_logic():
    keeper = sk.ScheduleKeeper(
        sched_fn=common.schedule_fn,
        override_queue=q
    )
    keeper.loop()


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/edit-schedule')
def sched():
    dat = '{}'
    if os.path.exists(common.schedule_fn):
        with open(common.schedule_fn, 'r') as f:
            dat = json.loads(f.read())
    return flask.render_template('schedule.html', schedule=dat)


@app.route('/edit-schedule', methods=['POST'])
def update_sched():
    new_schedule = flask.request.get_json()
    with open(common.schedule_fn, 'w') as f:
        f.write(json.dumps(new_schedule))
    return flask.redirect(flask.url_for('sched'))


@app.route('/override', methods=['POST'])
def override():
    ovr_dat = flask.request.get_json()
    try:
        st = ovr_dat['state']
        if st in (0, 1): q.put(st)
        else: q.put(None)
    except KeyError:
        logging.error('override dat corrupted')
    return flask.redirect(flask.url_for('sched'))


@app.route('/override', methods=['GET'])
def override_get():
    '''
    no reason for user to do a GET request but just in case
    someone tries it give them a happy message
    '''
    return '<!DOCTYPE html> <html><h1>gtfo</h1></html>'


if __name__ == '__main__':
    main()
