from text_helpers.text_tokenizer import token_to_sentence, token_to_words, read_mk_dictionary
from spellchecker.core_logic import edit_distance, edit_distance_1, edit_distance_2, calculate_suggestions_scores
import configuration
from services import language_model_service


MK_DICTIONARY = read_mk_dictionary(configuration.settings["dictionary_file_path"])


def spellcheck_text(text):

    analyzed_text_result = analyze_text(text, True)

    result = list()

    for analyzed_sentence_result in analyzed_text_result:

        analyzed_sentence = {
            "Original Sentence": analyzed_sentence_result["Original Sentence"],
            "Suggestions": list()
        }

        for word_suggestion in analyzed_sentence_result["Suggestions"]:

            word_suggestions_object = {
                "Original Word": word_suggestion["Word"],
                "Spelling": "Correct",
                "Suggestions": list()
            }

            if word_suggestion["Word"] == word_suggestion["Most Probable Word"]:
                analyzed_sentence["Suggestions"].append(word_suggestions_object)
                continue

            if is_valid_word(word_suggestion["Word"]):
                word_suggestions_object["Spelling"] = "Maybe Not Correct"
            else:
                word_suggestions_object["Spelling"] = "Not Correct"

            for suggestion in word_suggestion["Language Model Suggestions"]:
                if word_suggestion["Word"] != suggestion["Word"]:
                    word_suggestions_object["Suggestions"].append(suggestion["Word"])

            # if the word is 'Maybe Not Correct', we only use language model suggestions
            if word_suggestions_object["Spelling"] == "Maybe Not Correct":
                analyzed_sentence["Suggestions"].append(word_suggestions_object)
                continue

            for suggestion in word_suggestion["Single Word Suggestions"]:
                if word_suggestion["Word"] != suggestion["Word"]:
                    word_suggestions_object["Suggestions"].append(suggestion["Word"])

            analyzed_sentence["Suggestions"].append(word_suggestions_object)

        result.append(analyzed_sentence)

    return result


def analyze_text(text, detailed_response):

    sentences = token_to_sentence(text)

    print("Sentences={}".format(sentences))

    text_analyzer_result = list()

    for sentence_index, sentence in enumerate(sentences, start=1):
        sentence_analyzer_result = analyze_sentence(sentence, sentence_index, detailed_response)
        text_analyzer_result.append(sentence_analyzer_result)

    return text_analyzer_result


def analyze_sentence(sentence, sentence_index, detailed_response):

    words = token_to_words(sentence)

    result = {
        "Sentence index": sentence_index,
        "Original Sentence": sentence
    }

    previous_words_list = list()
    processed_suggestions_list = list()

    for index, word in enumerate(words, 0):

        if index == 0:
            suggestions = get_single_word_suggestions(word)
            suggestions_container = {
                "Word": word,
                "Most Probable Word": word,
                "Language Model Suggestions": list(),
                "Single Word Suggestions": suggestions
            }

            if len(suggestions) > 0:
                previous_words_list.append(suggestions[0]["Word"])
                suggestions_container["Most Probable Word"] = suggestions[0]["Word"]
            else:
                # nothing else to do in scenarios where there are no suggestions
                previous_words_list.append(word)

            processed_suggestions_list.append(suggestions_container)
            continue

        language_model_data = language_model_service.get_language_model_suggestions(previous_words_list)

        language_model_suggestions = calculate_suggestions_scores(word, language_model_data, detailed_response)

        word_suggestions_object = get_processed_suggestions(word, language_model_suggestions)

        update_previous_words_list(previous_words_list, word, language_model_suggestions, word_suggestions_object)

        processed_suggestions_list.append(word_suggestions_object)

    result["Top Suggestion"] = " ".join(previous_words_list)
    result["Suggestions"] = processed_suggestions_list

    return result


def get_single_word_suggestions(word):
    """

    :param word:
    :return:
    """

    words = list()

    word_is_valid = is_valid_word(word)

    if word_is_valid:
        words.append(word)

    edits1_words = edit_distance_1(word)
    edits2_words = edit_distance_2(edits1_words)

    # print("Word={}, Edits1Count={}, Edits2Count={}, Raw Words...".format(word, len(edits1_words), len(edits2_words)))

    edits1_words = set(word1 for word1 in edits1_words if is_valid_word(word1))
    edits2_words = set(word1 for word1 in edits2_words if is_valid_word(word1))

    # print("Word={}, Edits1Count={}, Edits2Count={}, Dictionary filtered Words...".format(word, len(edits1_words), len(edits2_words)))

    edits2_words = edits2_words.difference(edits1_words)

    # print("Word={}, Edits1Count={}, Edits2Count={}, Duplicate filtered Words...".format(word, len(edits1_words), len(edits2_words)))

    if word in edits1_words:
        edits1_words.remove(word)   # if the original word is present, remove it

    words.extend(edits1_words)
    words.extend(edits2_words)

    words_frequency = language_model_service.get_words_frequencies(words)

    result = list()
    if word_is_valid:
        result.append([word, 0, words_frequency[word]])

    result.extend([[word1, 1, words_frequency[word1]] for word1 in edits1_words])
    result.extend([[word1, 2, words_frequency[word1]] for word1 in edits2_words])

    result = sorted(result, key=lambda x: (x[1], -x[2]))
    result = result[:configuration.MAX_SUGGESTIONS_LIMIT]

    formatted_result = format_single_word_suggestions(result)

    return formatted_result


def format_single_word_suggestions(single_word_suggestions):
    result = list()

    for suggestion in single_word_suggestions:
        formatted_suggestion = {
            "Word": suggestion[0],
            "Edit Distance": suggestion[1],
            "Language Model Occurrences": suggestion[2]
        }

        result.append(formatted_suggestion)

    return result


def get_processed_suggestions(predicting_word, language_model_suggestions):

    top_lm_suggestions = [suggestion for suggestion in language_model_suggestions[:configuration.MAX_SUGGESTIONS_LIMIT]]

    word_suggestion_dict = {
        "Word": predicting_word,
        "Most Probable Word": predicting_word,
        "Language Model Suggestions": top_lm_suggestions,
        "Single Word Suggestions": list()
    }

    already_used_words = set(suggestion["Word"] for suggestion in top_lm_suggestions)

    if len(already_used_words) < configuration.MAX_SUGGESTIONS_LIMIT:
        single_word_suggestions = get_single_word_suggestions(predicting_word)

        for suggestion in single_word_suggestions:

            if suggestion["Word"] in already_used_words:
                continue

            already_used_words.add(suggestion["Word"])
            word_suggestion_dict["Single Word Suggestions"].append(suggestion)

            if len(already_used_words) >= configuration.MAX_SUGGESTIONS_LIMIT:
                break

    return word_suggestion_dict


def update_previous_words_list(previous_words_list, predicting_word, language_model_suggestions, word_suggestions_object):

    language_model_suggestions_count = len(language_model_suggestions)

    if language_model_suggestions_count == 0:
        # we have no language model suggestions, check single word suggestions

        if len(word_suggestions_object) > 0 and word_suggestions_object["Single Word Suggestions"][0]["Edit Distance"] <= 1:
            previous_words_list.append(word_suggestions_object["Single Word Suggestions"][0]["Word"])
            word_suggestions_object["Most Probable Word"] = word_suggestions_object["Single Word Suggestions"][0]["Word"]
            return

        # if no single word suggestions exist that are at most 1 edit distance from our word, use the predicting word
        previous_words_list.append(predicting_word)
        return

    if check_if_suggestions_contains_predicting_word(predicting_word, language_model_suggestions):
        previous_words_list.append(predicting_word)
        return

    top_suggestion = language_model_suggestions[0]

    previous_words_list.append(top_suggestion["Word"])
    word_suggestions_object["Most Probable Word"] = top_suggestion["Word"]

    print("PredictingWord={}, TopSuggestion={}, Message=\"Swapping predicting word with top suggestion in previous words list.\""
          .format(predicting_word, top_suggestion["Word"]))


def check_if_suggestions_contains_predicting_word(predicting_word, language_model_suggestions):
    """

    :param predicting_word:
    :param language_model_suggestions:
    :return:
    """

    for suggestion in language_model_suggestions: # Check if this needs to be limited to check only top 100
        if suggestion["Word"] == predicting_word:
            return True

    return False


def is_valid_word(word):
    return word in MK_DICTIONARY
