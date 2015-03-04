import os
import json
import gevent
from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for
from flask import send_file, make_response, abort
from flask.ext.restful import reqparse, abort, Api, Resource


from ouimeaux.signals import statechange
from ouimeaux.device.switch import Switch
from ouimeaux.device.insight import Insight
from ouimeaux.device.maker import Maker
from ouimeaux.environment import Environment, UnknownDevice
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

here = lambda *x: os.path.join(os.path.dirname(__file__), *x)


app = Flask(__name__)
api = Api(app)

ENV = None


def initialize(bind=None):
    global ENV
    if ENV is None:
        ENV = Environment(with_cache=False, bind = bind)
        ENV.start()
        gevent.spawn(ENV.discover, 10)


def serialize(device):
    if isinstance(device, Insight):
      return {'name': device.name,
              'type': device.__class__.__name__,
              'serialnumber': device.serialnumber,
              'state': device.get_state(),
              'model': device.model,
              'host': device.host,
              'lastchange': str(device.last_change),
              'onfor': device.on_for,
              'ontoday': device.today_on_time,
              'ontotal': device.ontotal,
              'todaymw': device.today_kwh,
              'totalmw': device.totalmw,
              'currentpower': device.current_power
              }
    elif isinstance(device, Maker):
       return {'name': device.name,
              'type': device.__class__.__name__,
              'serialnumber': device.serialnumber,
              'state': device.get_state(),
              'model': device.model,
              'host': device.host,
              'hassensor' : device.has_sensor,
              'switchmode' : device.switch_mode,
              'sensor' : device.sensor_state
              }
    return {'name': device.name,
            'type': device.__class__.__name__,
            'serialnumber': device.serialnumber,
            'state': device.get_state(),
            'model': device.model,
            'host': device.host}


def get_device(name, should_abort=True):
    try:
        return ENV.get(name)
    except UnknownDevice:
        if not should_abort:
            raise
        abort(404, error='No device matching {}'.format(name))


# First, the REST API
class EnvironmentResource(Resource):

    def get(self):
        result = {}
        for dev in ENV:
            result[dev.name] = serialize(dev)
        return result

    def post(self):
        seconds = (request.json or {}).get('seconds', (
            request.values or {}).get('seconds', 5))
        ENV.discover(int(seconds))
        return self.get()


class DeviceResource(Resource):

    def get(self, name):
        return serialize(get_device(name))

    def post(self, name):
        dev = get_device(name)
        if not isinstance(dev, Switch):
            abort(405, error='Only switches can have their state changed')
        action = (request.json or {}).get('state', (
            request.values or {}).get('state', 'toggle'))
        if action not in ('on', 'off', 'toggle', 'blink'):
            abort(400, error='{} is not a valid state'.format(action))
        if action == 'blink':
            delay = (request.json or {}).get('delay', (
                request.values or {}).get('delay', '1'))
            getattr(dev, action)(delay=int(delay))
        else:
            getattr(dev, action)()
        return serialize(dev)


api.add_resource(EnvironmentResource, '/api/environment')
api.add_resource(DeviceResource, '/api/device/<string:name>')


class SocketNamespace(BaseNamespace):

    def update_state(self, sender, **kwargs):
        data = serialize(sender)
        data['state'] = kwargs.get('state', data['state'])
        self.emit("send:devicestate", data)

    def on_statechange(self, data):
        ENV.get(data['name']).set_state(data['state'])

    def on_join(self, data):
        statechange.connect(self.update_state,
                            unique=False,
                            dispatch_uid=id(self))
        for device in ENV:
            self.update_state(device)

    def __del__(self):
        statechange.disconnect(dispatch_uid=id(self))


# Now for the WebSocket api
@app.route("/socket.io/<path:path>")
def run_socketio(**kwargs):
    socketio_manage(request.environ, {'': SocketNamespace})


# routing for basic pages (pass routing onto the Angular app)
@app.route('/')
def basic_pages(**kwargs):
    return make_response(open(here('templates/index.html')).read())


# special file handlers and error handlers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'img/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.config.from_object('ouimeaux.server.settings')
app.url_map.strict_slashes = False

if __name__ == "__main__":
    app.run()
