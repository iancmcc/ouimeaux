import os
import json
import gevent
from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for
from flask import send_file, make_response, abort
from flask.ext.restful import reqparse, abort, Api, Resource


from ouimeaux.device.switch import Switch
from ouimeaux.environment import Environment, UnknownDevice


app = Flask(__name__)
api = Api(app)

ENV = None


def initialize():
    global ENV
    if ENV is None:
        ENV = Environment(with_cache=False)
        ENV.start()
        gevent.spawn(ENV.discover, 10)


def serialize(device):
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
        action = request.json.get('state', request.values.get(
            'state', 'toggle'))
        if action not in ('on', 'off', 'toggle'):
            abort(400, error='{} is not a valid state'.format(action))
        getattr(dev, action)()
        return serialize(dev)


api.add_resource(EnvironmentResource, '/api/environment')
api.add_resource(DeviceResource, '/api/device/<string:name>')


# Now for the WebSocket api


# routing for basic pages (pass routing onto the Angular app)
@app.route('/')
@app.route('/about')
def basic_pages(**kwargs):
    return make_response(open('templates/index.html').read())


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
