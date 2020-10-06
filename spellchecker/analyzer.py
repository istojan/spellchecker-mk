from text_helpers.text_tokenizer import token_to_sentence, token_to_words, read_mk_dictionary, is_special_word
from spellchecker.core_logic import edit_distance, edit_distance_1_new, edit_distance_2, calculate_suggestions_scores
import configuration
from services import language_model_service
import time


MK_DICTIONARY = read_mk_dictionary(configuration.settings["dictionary_file_path"])


def analyze_text_by_words_breakdown(text):

    analyzed_text_result = analyze_text(text, True)

    words_breakdown_result = list()

    for analyzed_sentence_result in analyzed_text_result:

        # analyzed_sentence = {
        #     "Original Sentence": analyzed_sentence_result["Original Sentence"],
        #     "Suggestions": list()
        # }

        for word_suggestion in analyzed_sentence_result["Suggestions"]:

            word_suggestions_object = {
                "Збор": word_suggestion["Word"]
            }

            if word_suggestion["Word"] == word_suggestion["Most Probable Word"]:
                # analyzed_sentence["Suggestions"].append(word_suggestions_object)
                # print(word_suggestion)
                words_breakdown_result.append(word_suggestions_object)
                continue

            if is_valid_word(word_suggestion["Word"]):
                word_suggestions_object["Тип на предлог"] = "Можеби грешка"
            else:
                word_suggestions_object["Тип на предлог"] = "Грешка"

            word_suggestions_object["Предлози"] = list()

            for suggestion in word_suggestion["Language Model Suggestions"]:
                if word_suggestion["Word"] != suggestion["Word"]:
                    word_suggestions_object["Предлози"].append(suggestion["Word"])

            # if the word is 'Maybe Not Correct', we only use language model suggestions
            if word_suggestions_object["Тип на предлог"] == "Можеби грешка":
                # analyzed_sentence["Suggestions"].append(word_suggestions_object)
                words_breakdown_result.append(word_suggestions_object)
                continue

            for suggestion in word_suggestion["Single Word Suggestions"]:
                if word_suggestion["Word"] != suggestion["Word"]:
                    word_suggestions_object["Предлози"].append(suggestion["Word"])

            # analyzed_sentence["Suggestions"].append(word_suggestions_object)
            words_breakdown_result.append(word_suggestions_object)

        # result.append(analyzed_sentence)
        words_breakdown_result.append({
            "Збор": analyzed_sentence_result["Sign"]
        })

    return words_breakdown_result


def analyze_text(text, detailed_response):

    total_start_time = time.time()

    sentences_and_signs = token_to_sentence(text)
    sentences_count = len(sentences_and_signs)

    text_analyzer_result = list()

    print("SentencesCount={}, Messages=\"Starting to analyze sentences.\"".format(sentences_count))

    for sentence, sign in sentences_and_signs:

        if sentence is "":
            text_analyzer_result.append({
                "Original Sentence": "{}".format(sign),
                "Top Suggestion": "{}".format(sign),
                "Suggestions": list(),
                "Sign": sign
            })
            continue

        start_time = time.time()
        sentence_analyzer_result = analyze_sentence(sentence, detailed_response)
        sentence_analyzer_result["Top Suggestion"] = " " + sentence_analyzer_result["Top Suggestion"] + sign
        sentence_analyzer_result["Original Sentence"] = " " + sentence_analyzer_result["Original Sentence"] + sign
        sentence_analyzer_result["Sign"] = sign
        text_analyzer_result.append(sentence_analyzer_result)

        print("ElapsedTime={}, Message=\"Sentences analyzed.\"".format(time.time() - start_time, sentences_count))

    print("TotalElapsedTime={}, SentencesCount={}, Messages=\"Finished analyzing sentences.\"".format(time.time() - total_start_time, sentences_count))

    return text_analyzer_result


# TODO: add logic for names, numbers...
def analyze_sentence(sentence, detailed_response):

    words = token_to_words(sentence)

    result = {
        "Original Sentence": sentence
    }

    previous_words_list = list()
    processed_suggestions_list = list()

    for index, original_word in enumerate(words, 0):

        word = original_word.lower()

        start_time = time.time()

        # check if this should stay
        if len(word) == 1:
            processed_suggestions_list.append(get_default_word_suggestion(word))
            previous_words_list.append(word)
            continue

        if is_special_word(word):
            # word is either name or digit
            processed_suggestions_list.append(get_default_word_suggestion(word))
            previous_words_list.append(word)
            continue

        if index == 0:
            suggestions = get_single_word_suggestions(word)
            suggestions_container = {
                "Word": original_word,
                "Most Probable Word": original_word,
                "Language Model Suggestions": list(),
                "Single Word Suggestions": suggestions
            }

            if len(suggestions) > 0:
                previous_words_list.append(suggestions[0]["Word"])
                suggestions_container["Most Probable Word"] = suggestions[0]["Word"]
            else:
                # nothing else to do in scenarios where there are no suggestions
                previous_words_list.append(word)

            if not original_word.islower():
                suggestions_container["Most Probable Word"] = suggestions_container["Most Probable Word"].capitalize()

            processed_suggestions_list.append(suggestions_container)
            print("ElapsedTime={}, Building first word suggestion elapsed time".format(time.time() - start_time))
            continue

        language_model_data = language_model_service.get_language_model_suggestions(previous_words_list)

        language_model_suggestions = calculate_suggestions_scores(word, language_model_data, detailed_response)

        word_suggestions_object = get_processed_suggestions(word, language_model_suggestions)

        update_previous_words_list(previous_words_list, word, language_model_suggestions, word_suggestions_object)

        processed_suggestions_list.append(word_suggestions_object)

    # result["Top Suggestion"] = " ".join(previous_words_list)
    result["Top Suggestion"] = " ".join(suggestion["Most Probable Word"] for suggestion in processed_suggestions_list)
    result["Suggestions"] = processed_suggestions_list

    return result


def get_default_word_suggestion(word):
    word_suggestion = {
        "Word": word,
        "Most Probable Word": word,
        "Language Model Suggestions": list(),
        "Single Word Suggestions": list()
    }

    return word_suggestion


def get_single_word_suggestions(word):
    """

    :param word:
    :return:
    """

    words = set()

    word_is_valid = is_valid_word(word)

    if word_is_valid:
        words.add(word)

    edits1_words = edit_distance_1_new(word)
    edits2_words = edit_distance_2(edits1_words)

    edits1_words = set(word1 for word1 in edits1_words if is_valid_word(word1))
    edits2_words = set(word1 for word1 in edits2_words if is_valid_word(word1))

    edits2_words = edits2_words.difference(edits1_words)

    # if the original word is present, remove it
    if word in edits1_words:
        edits1_words.remove(word)

    if word in edits2_words:
        edits2_words.remove(word)

    words.update(edits1_words)
    words.update(edits2_words)

    words_frequency = language_model_service.get_words_frequencies(list(words))

    result = list()
    if word_is_valid:
        result.append([word, 0, words_frequency[word]])

    result.extend([[word1, 1, words_frequency[word1]] for word1 in edits1_words])
    result.extend([[word2, 2, words_frequency[word2]] for word2 in edits2_words])

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

    # investigate why this is sooooo slow. Merge this with the language model call.
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

        if len(word_suggestions_object["Single Word Suggestions"]) > 0 and word_suggestions_object["Single Word Suggestions"][0]["Edit Distance"] <= 1:
            previous_words_list.append(word_suggestions_object["Single Word Suggestions"][0]["Word"])
            word_suggestions_object["Most Probable Word"] = word_suggestions_object["Single Word Suggestions"][0]["Word"]
            return

        # if no single word suggestions exist that are at most 1 edit distance from our word, use the predicting word
        previous_words_list.append(predicting_word)
        return

    if check_if_suggestions_contains_predicting_word(predicting_word, language_model_suggestions):
        previous_words_list.append(predicting_word)
        return

    # this is optional
    single_words = set([sugg["Word"] for sugg in word_suggestions_object["Single Word Suggestions"]])
    if predicting_word in single_words:
        previous_words_list.append(predicting_word)
        return

    top_suggestion = language_model_suggestions[0]

    previous_words_list.append(top_suggestion["Word"])
    word_suggestions_object["Most Probable Word"] = top_suggestion["Word"]

    # print("PredictingWord={}, TopSuggestion={}, Message=\"Swapping predicting word with top suggestion in previous words list.\""
    #       .format(predicting_word, top_suggestion["Word"]))


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
