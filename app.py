import os
from flask import Flask

# creates and configures the app (aka application factory)
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # apply blueprints to app
    from Stocking import analysis, tool
    app.register_blueprint(analysis.bp)
    app.register_blueprint(tool.bp)

    # index is homepage
    app.add_url_rule('/', endpoint='/index')

if __name__ == '__main__:
    app.run()
