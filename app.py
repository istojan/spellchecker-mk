from flask import Flask
from flask import request
from spellchecker.analyzer import analyze_text
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/check")
def analyze_sentence():

    text = request.args["text"]

    detailed_response = False

    if "detailed" in request.args:
        detailed_response = request.args["detailed"]



    print("Text={}, Message=\"Received a request to check spelling for text.\"".format(text))

    result = analyze_text(text, detailed_response)

    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001)
