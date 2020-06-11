from configuration import settings
import sys
from text_helpers import text_tokenizer
from random import randint
import csv


CHANGE_CHARACTER_PROBABILITY_PERCENTAGE = 7

ALPHABET = "абвгдѓежзѕијклљмнњопрстќуфхцчџш"


def create_error_from_character(original_character):
    """
    We can produce 3 types of errors:
    - add extra character
    - delete character
    - change character into a new character

    We would use all 3 errors. Since the most common mistake is probably using a different letter, 50% of the errors
    would be of the 3rd type and 25% would be from the 1st and 2th

    :param original_character:
    :return:
    """

    error_type_int = randint(0, 100)

    # if random number is less than 25, we add an extra character
    if error_type_int <= 25:
        return original_character + "" + get_random_alphabet_character()
    # if random is between 25-50, we delete the character
    elif error_type_int <= 50:
        return ""
    # if random number is between 51-100, we change the character into a different character
    else:
        return get_random_alphabet_character(original_character)


def get_random_alphabet_character(original_character=""):
    """
    A method to generate a random character. If an original_character is passed, we want to return a random character
    that is not the original character.
    :param original_character:
    :return:
    """

    while True:
        random_index = randint(1, len(ALPHABET))

        if ALPHABET[random_index-1] != original_character:
            return ALPHABET[random_index-1]


def read_input_file(input_file_path):

    text = ""

    with open(input_file_path, 'r') as input_file:

        for line in input_file:
            text += line.replace("\n", " ")

    return text


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
            if c.isalpha() and randint(0, 100) < CHANGE_CHARACTER_PROBABILITY_PERCENTAGE:
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
            original_sentence_words = text_tokenizer.token_to_words(original_sentences_list[sentence_idx])
            error_sentence_words = text_tokenizer.token_to_words(error_containing_sentences_list[sentence_idx])

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
