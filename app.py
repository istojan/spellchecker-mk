from flask import Flask
from flask import request
from flask import jsonify
from spellchecker import analyzer


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/check")
def analyze_sentence():

    text = request.args["text"]
    detailed_response = request.args.get("detailed", False)

    result = analyzer.analyze_text(text, detailed_response)

    return jsonify(result)


@app.route("/check/text")
def spellcheck_text():

    text = request.args["text"]

    spellcheck_text_result = analyzer.spellcheck_text(text)

    return jsonify(spellcheck_text_result)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001)
