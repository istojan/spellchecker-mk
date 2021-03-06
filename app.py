from flask import Flask
from flask import request
from flask import jsonify
from spellchecker import analyzer
from cache.names import initialize_names_cache


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/check/text/sentences")
def analyze_text_by_sentences():

    text = request.args["text"]
    detailed_response = request.args.get("detailed", False)

    result = analyzer.analyze_text(text, detailed_response)

    return jsonify(result)


@app.route("/check/text/complete")
def analyze_complete_text():

    text = request.args["text"]
    detailed_response = request.args.get("detailed", False)

    result = analyzer.analyze_text(text, detailed_response)

    response = {
        "Original Text": "",
        "Corrected Text": ""
    }

    for item in result:
        response["Original Text"] = response["Original Text"] + item["Original Sentence"]
        response["Corrected Text"] = response["Corrected Text"] + item["Top Suggestion"]

    response["Original Text"] = response["Original Text"].strip()
    response["Corrected Text"] = response["Corrected Text"].strip()

    return jsonify(response)


@app.route("/check/text")
def analyze_text_by_words_breakdown():

    text = request.args["text"]

    spellcheck_text_result = analyzer.analyze_text_by_words_breakdown(text)

    return jsonify(spellcheck_text_result)


if __name__ == '__main__':

    initialize_names_cache()

    app.run(host="127.0.0.1", port=5001)

# to check
# "Sentence index": 6,
# "Original Sentence": "Ова е глуп тексчт што нема апсолутгно никакво значење и оди до безкрај",
# "Top Suggestion": "ова е глас текст што не апсолутно никакво значење и да до бескрај",
# "Suggestions": [

# TODO: make most probable word select from single word suggestions if no alternatives exist:
# example:
# "Original Sentence": "Мартин е таковњ непријатен човек што никој не се хуствува безбедно во ноегова близина",
# "Top Suggestion": "мартин е таков непријатен ѕвек што никој не се хуствува безбедно во негова близина",