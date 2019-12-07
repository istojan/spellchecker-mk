import requests
from text_helpers.text_tokenizer import token_to_sentence, token_to_words, read_mk_dictionary
from spellchecker.core_logic import edit_distance, edit_distance_1, edit_distance_2, calculate_suggestions_scores
from operator import itemgetter
from configuration import settings


MK_DICTIONARY = read_mk_dictionary(settings["dictionary_file_path"])


def analyze_text(text, detailed_response):

    sentences = token_to_sentence(text)

    print("Sentences={}".format(sentences))

    text_analyzer_result = dict()

    for sentence_index, sentence in enumerate(sentences, start=1):
        sentence_analyzer_result = analyze_sentence(sentence, detailed_response)
        text_analyzer_result[sentence_index] = sentence_analyzer_result

    return text_analyzer_result


def analyze_sentence(sentence, detailed_response):

    words = token_to_words(sentence)

    result = {
        "Sentence": sentence,
        "Suggestions": list()
    }

    tmp_word_list = list()

    for index, word in enumerate(words, 0):

        tmp_word_list.append(word)

        if index == 0:
            suggestions = get_single_word_suggestions(word)
            result["Suggestions"].append([word, suggestions])
            continue

        mini_sentence = " ".join(tmp_word_list[:-1])

        r = requests.get('http://127.0.0.1:5000/model/query', params={"sentence": mini_sentence})
        language_model_data = r.json()
        language_model_suggestions = calculate_suggestions_scores(word, language_model_data, detailed_response)

        print("Sentence={}, ResponseCount={}".format(mini_sentence, len(language_model_data)))

        top_suggestions = language_model_suggestions[:3]
        #
        # for suggestion in language_model_data:
        #     distance = edit_distance(word, suggestion[0], len(word), len(suggestion[0]))
        #     level = suggestion[2]
        #
        #     score = distance + level
        #
        #     if score <= 4:
        #         top_suggestions.append([suggestion[0], distance, level, score])
        #
        # top_suggestions = sorted(top_suggestions, key=itemgetter(3))

        result["Suggestions"].append([word, [suggestion for suggestion in top_suggestions[:10]]])
        # json_data = json.loads(r.text, ensure_ascii=False)
        # json_data = json.loads(r.text)

        # print("Sentence={}, Response={}".format(mini_sentence, r.text))

        # suggestions = json.load(r.text)

        # print(suggestions)

        word_suggestions = list()

    return result


def get_single_word_suggestions(word):

    result = list()

    if word in MK_DICTIONARY:
        result.append([word, 0])

    edits1_words = edit_distance_1(word)
    edits2_words = edit_distance_2(edits1_words)

    print("Word={}, Edits1Count={}, Edits2Count={}, Raw Words...".format(word, len(edits1_words), len(edits2_words)))

    edits1_words = set(word1 for word1 in edits1_words if word1 in MK_DICTIONARY)
    edits2_words = set(word1 for word1 in edits2_words if word1 in MK_DICTIONARY)

    print("Word={}, Edits1Count={}, Edits2Count={}, Dictionary filtered Words...".format(word, len(edits1_words), len(edits2_words)))

    edits2_words = edits2_words.difference(edits1_words)

    print("Word={}, Edits1Count={}, Edits2Count={}, Duplicate filtered Words...".format(word, len(edits1_words), len(edits2_words)))

    if word in edits1_words:
        edits1_words.remove(word)   # if the original word is present, remove it

    result.extend([[word1, 1] for word1 in edits1_words])
    result.extend([[word1, 2] for word1 in edits2_words])

    result = sorted(result, key=itemgetter(1))

    return result[:10]
    # return list(edits1_words)



