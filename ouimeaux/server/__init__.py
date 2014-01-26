import os
import json
from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for
from flask import send_file, make_response, abort

app = Flask("ouimeaux.server")

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
