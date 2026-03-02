import uuid
from flask import g

def attach_request_id(app):

    @app.before_request
    def generate_request_id():
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def add_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response