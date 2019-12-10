import requests
import json
from configuration import settings


def get_words_frequencies(words):

    request_address = get_language_model_service_url("model/words/frequency")

    response = requests.get(request_address, params={"words": json.dumps(words)})
    words_frequency = response.json()

    return words_frequency


def get_language_model_suggestions(previous_words):
    previous_words_sentence = " ".join(previous_words)

    request_address = get_language_model_service_url("model/query")
    r = requests.get(request_address, params={"sentence": previous_words_sentence})
    language_model_data = r.json()

    return language_model_data


def get_language_model_service_url(path):
    return "{}/{}".format(settings["language_model_service_address"], path)
