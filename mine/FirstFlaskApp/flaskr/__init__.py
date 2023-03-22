# import dependencies
from flask import Flask, jsonify
#define create app function
def create_app(test_config=None):
    # create and configure the app
    # Include the first parameter: Here, __name__ is the name of the 
    # current Python module

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return jsonify({'message':'Hello, World!'})


    @app.route('/smiley')
    def smiley():
        return ':}'

    # return the app instance
    return app

