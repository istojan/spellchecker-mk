from configuration import settings
import sys
from text_helpers import text_tokenizer
from random import randint
import csv


CHANGE_CHARACTER_PROBABILITY_PERCENTAGE = 7

ALPHABET = "абвгдѓежзѕијклљмнњопрстќуфхцчџш"

CHARACTER_TO_ERROR_COMBINATIONS = {
    "а": ["с", "њ", "љ", "з", "џ"],
    "б": ["в", "г", "х", "н", "п"],
    "в": ["ц", "ф", "г", "б"],
    "г": ["ф", "т", "ѕ", "х", "б", "в", "ѓ"],
    "д": ["џ", "с", "е", "р", "ф", "ц", "т"],
    "ѓ": ["ж", "ќ", "ш", "г"],
    "е": ["р", "д", "с", "њ"],
    "ж": ["ќ", "ѓ", "ш", "з"],
    "з": ["џ", "с", "а"],
    "ѕ": ["у", "х", "г", "т"],
    "и": ["о", "к", "ј", "у"],
    "ј": ["н", "х", "у", "и", "к", "м"],
    "к": ["м", "ј", "и", "о", "л"],
    "л": ["к", "о", "п", "ч", "љ"],
    "љ": ["њ", "а", "л"],
    "м": ["н", "ј", "к"],
    "н": ["б", "х", "ј", "м", "њ"],
    "њ": ["е", "с", "а", "љ"],
    "о": ["п", "ч", "л", "к", "и"],
    "п": ["ш", "ч", "л", "о", "б"],
    "р": ["т", "ф", "д", "е"],
    "с": ["д", "џ", "з", "а", "њ", "е"],
    "т": ["ѕ", "х", "г", "ф", "р"],
    "ќ": ["ш", "ѓ", "ж", "ч", "к"],
    "у": ["и", "к", "ј", "х", "ѕ"],
    "ф": ["ц", "д", "р", "т", "г", "в"],
    "х": ["б", "г", "ѕ", "у", "ј", "н"],
    "ц": ["џ", "д", "ф", "в"],
    "ч": ["л", "п", "ш", "ќ", "џ"],
    "џ": ["з", "с", "д", "ц", "ч"],
    "ш": ["ѓ", "ж", "ќ", "ч", "п", "с"]
}


def create_error_from_character(original_character):
    """
    We can produce 3 types of errors:
    - add extra character
    - delete character
    - change character into a different character

    We would use all 3 errors. Since the most common mistake is probably using a different letter, 50% of the errors
    would be of the 3rd type and 25% would be from the 1st and 2th

    :param original_character:
    :return:
    """

    is_upper = original_character.isupper()

    error_type_int = randint(1, 100)

    # if random number is less than 25, we add an extra character
    if error_type_int <= 25:
        error = original_character + "" + get_related_character(original_character, is_same_character_allowed=True)
    # if random is between 25-50, we delete the character
    elif error_type_int <= 50:
        error = ""
    # if random number is between 51-100, we change the character into a different character
    else:
        error = get_related_character(original_character, is_same_character_allowed=False)

    if is_upper:
        return error.upper()

    return error.lower()


def get_related_character(original_character, is_same_character_allowed=True):
    """
    A method to generate a related character to the original. The combinations of characters are defined in
    CHARACTER_TO_ERROR_COMBINATIONS. Besides the characters mentioned there, another option is to return the same character
    :param original_character:
    :return:
    """

    related_char = ""

    char_combinations = CHARACTER_TO_ERROR_COMBINATIONS[original_character.lower()]
    total_char_combinations = len(char_combinations)

    while not related_char:
        related_char_position = randint(0, total_char_combinations)

        if is_same_character_allowed and related_char_position == total_char_combinations:
            related_char = original_character

        if related_char_position < total_char_combinations:
            related_char = char_combinations[related_char_position]

    return related_char


def read_input_file(input_file_path):

    text = ""

    with open(input_file_path, 'r') as input_file:

        for line in input_file:
            text += line.replace("\n", " ")

    return text


def is_cyrilic_character(char):

    if not char.isalpha():
        return False

    return (char >= 'а' and char <= "ш") or (char >= "А" and char  <= "Ш")


if __name__ == '__main__':

    if "validation_system_files_directory" not in settings:
        print("Need to define a file path under key 'validation_system_files_directory' key that will be used for testing.")
        sys.exit()

    if "validation_system_input_file_name" not in settings:
        print("Need to define a file path under key 'validation_system_input_file_name' key that will be used for testing.")
        sys.exit()

    validation_system_files_directory = settings["validation_system_files_directory"]

    input_file_path = validation_system_files_directory + settings["validation_system_input_file_name"]

    output_errors_file_path = validation_system_files_directory + "errors_text.txt"
    output_errors_audit_log_file_path = validation_system_files_directory + "errors_audit_log.txt"

    idx = 0

    text = read_input_file(input_file_path)

    with open(output_errors_file_path, 'w') as output_error_file, open(output_errors_audit_log_file_path, 'w') as output_audit_log_file:
        audit_log_file_tsv = csv.writer(output_audit_log_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        audit_log_file_tsv.writerow(["ErrorAdded", "Word", "ErrorWord"])

        output_text = ""

        for c in text:
            if is_cyrilic_character(c) and randint(0, 100) < CHANGE_CHARACTER_PROBABILITY_PERCENTAGE:
                characters_to_replace = create_error_from_character(c)
                print("Changing {} to {}".format(c, characters_to_replace))
                output_text += characters_to_replace
            else:
                output_text += c

        original_sentences_list = text_tokenizer.token_to_sentence(text)
        error_containing_sentences_list = text_tokenizer.token_to_sentence(output_text)

        if len(original_sentences_list) != len(error_containing_sentences_list):
            print("Different number of sentences...")
            sys.exit()

        for sentence_idx in range(0, len(original_sentences_list)):
            original_sentence_words = text_tokenizer.token_to_words(original_sentences_list[sentence_idx][0])
            error_sentence_words = text_tokenizer.token_to_words(error_containing_sentences_list[sentence_idx][0])

            if len(original_sentence_words) != len(error_sentence_words):
                print("OriginalSentencesWordCount={}, ErrorSentencesWordCount={}, Different number of words..."
                      .format(len(original_sentence_words), len(error_sentence_words)))
                continue

            for word_idx in range(0, len(original_sentence_words)):
                original_word = original_sentence_words[word_idx]
                error_word = error_sentence_words[word_idx]

                audit_log_file_tsv.writerow([original_word != error_word, original_word, error_word])
                # output_audit_log_file.write("Different: {}, Original: {}, Error: {}\n".format(original_word != error_word, original_word, error_word))

        output_error_file.write(output_text)
