from flask import jsonify
from flask_cors import CORS

from config import Parser
from flask import Flask
from routes.api_v1 import bp as api_v1_bp

config = Parser()

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"*": {"origins": "*"}})
app.config.update({
    'SECRET_KEY': config.get("api", "secret_key", "secret"),
})


# Create tables if they do not exist already
@app.before_first_request
def create_tables():
    # You can add here a script to init the database
    pass


app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
app.debug = config.get("api", "debug", False)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    response = jsonify({"msg": str(error)})
    print(str(error))
    response.status_code = error.code
    return response


if __name__ == "__main__":
    port = int(config.get("api", "port", 8000))
    debug = config.get("api", "debug", False)
    app.run(host='0.0.0.0', port=port, debug=debug)

