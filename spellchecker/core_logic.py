from configuration import MAX_ALLOWED_EDIT_DISTANCE, N_GRAM_LEVEL, LANGUAGE_MODEL_PTS_PER_LEVEL, LETTERS
from operator import itemgetter


# A Dynamic Programming based Python program for edit
# distance problem 
def edit_distance(str1, str2, m, n):
    # Create a table to store results of subproblems 
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # Fill d[][] in bottom up manner 
    for i in range(m + 1):
        for j in range(n + 1):

            # If first string is empty, only option is to 
            # insert all characters of second string 
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # If second string is empty, only option is to 
            # remove all characters of second string 
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # If last characters are same, ignore last char 
            # and recur for remaining string 
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

                # If last character are different, consider all
            # possibilities and find minimum 
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # Insert
                                   dp[i - 1][j],  # Remove
                                   dp[i - 1][j - 1])  # Replace

    return dp[m][n]


def edit_distance_1(word):
    "All edits that are one edit away from `word`."

    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in LETTERS]
    inserts = [L + c + R for L, R in splits for c in LETTERS]

    return set(deletes + transposes + replaces + inserts)


def edit_distance_2 (edit_distance_1_words):
    "All edits that are two edits away from `word`."
    return set(e2 for e1 in edit_distance_1_words for e2 in edit_distance_1(e1))


def calculate_suggestions_scores(original_word, language_model_data, detailed_response):
    """

    :param original_word:
    :param language_model_data:
    :return:
    """

    result = list()

    if len(language_model_data) == 0:
        return result

    min_frequencies_per_level, max_frequencies_per_level = extract_min_max_frequency_values(language_model_data)

    for suggestion_word, frequency, level in language_model_data:
        # 3 2 1 values
        frequency_normalized, frequency_score = get_normalized_frequency_and_score(frequency, min_frequencies_per_level[level], max_frequencies_per_level[level])

        edit_distance_value = edit_distance(original_word, suggestion_word, len(original_word), len(suggestion_word))

        if edit_distance_value >= MAX_ALLOWED_EDIT_DISTANCE:
            continue

        total_suggestion_score, edit_distance_score, language_model_level_score = calculate_suggestion_score(edit_distance_value, frequency_score, level)

        suggestion = {
            "Word": suggestion_word,
            "Total Score": total_suggestion_score
        }
        if detailed_response:
            suggestion["Edit Distance Score"] = edit_distance_score
            suggestion["Edit Distance Value"] = edit_distance_value
            suggestion["Frequency Score"] = frequency_score
            suggestion["Language Model Score"] = language_model_level_score
            suggestion["Frequency Normalized"] = frequency_normalized
            suggestion["Frequency"] = frequency
            suggestion["Level Score"] = level

        result.append(suggestion)
        # result.append([suggestion_word, total_suggestion_score, edit_distance_score, frequency_score, language_model_level_score, edit_distance_value, frequency_normalized, frequency, level])

    result = sorted(result, key=itemgetter("Total Score"), reverse=True)

    return result


def extract_min_max_frequency_values(language_model_data):
    """
    TODO
    :param language_model_data: a list of tuples of suggestions from the language model service.
    One tuple consists of: [word_suggestion, frequency_of_word, language_model_level]
    :return:
    """

    min_frequencies_per_level = dict()
    max_frequencies_per_level = dict()

    for word, frequency, level in language_model_data:
        if level not in min_frequencies_per_level:
            min_frequencies_per_level[level] = frequency
        else:
            min_frequencies_per_level[level] = min(frequency, min_frequencies_per_level[level])

        if level not in max_frequencies_per_level:
            max_frequencies_per_level[level] = frequency
        else:
            max_frequencies_per_level[level] = max(frequency, max_frequencies_per_level[level])

    return min_frequencies_per_level, max_frequencies_per_level


def get_normalized_frequency_and_score(frequency, min_frequency, max_frequency):
    """
    TODO
    :param frequency:
    :param min_frequency:
    :param max_frequency:
    :return:
    """

    if max_frequency == min_frequency:
        frequency_normalized = 1
    else:
        frequency_normalized = (frequency - min_frequency) / (max_frequency - min_frequency)

    if frequency_normalized > 2/3:
        frequency_score = 3
    elif frequency_normalized >= 1/3:
        frequency_score = 2
    else:
        frequency_score = 1

    return frequency_normalized, frequency_score


def calculate_suggestion_score(edit_distance_value, frequency_score, level):
    """
    A function that calculates an aggregated scoring on a spelling suggestion. A higher score means that the suggestion
    has a higher chance of being selected (only the suggestions with the highest scores are offered as suggestions
    to the user).

    The following scores have an effect in the total score:
    - edit_distance_score - calculated from the edit_distance with a value between 2-(maximum edit distance + 1)
    allowed to be considered. A maximum score means that the original and suggested word have an edit_distance = 1
    - frequency_score - calculated by normalizing the frequency scores and grouping them in 3 groups by using the
    normalized frequency. A frequency of 3 means that it has a higher frequency of appearing, while a frequency of 1
    means it has the lowest frequency of appearing
    - language_model_level_score - calculated from the level of the language model where this prediction was found.
    This can have a value between 0:(N_GRAM_LEVEL-2)*LANGUAGE_MODEL_PTS_PER_LEVEL

    :param edit_distance_value:
    :param frequency_score: a value between 1:3
    :param level: a value between 1:(N-GRAM level - 1)
    :return:
    """

    edit_distance_score = MAX_ALLOWED_EDIT_DISTANCE - edit_distance_value + 2 # a value between 2:MAX_ALLOWED_EDIT_DISTANCE+1
    language_model_level_score = get_language_model_level_score(level)

    return edit_distance_score + frequency_score + language_model_level_score, edit_distance_score, language_model_level_score


def get_language_model_level_score(level):
    """
    TODO
    :param level:
    :return:
    """


    return LANGUAGE_MODEL_PTS_PER_LEVEL * (N_GRAM_LEVEL - level - 1)
