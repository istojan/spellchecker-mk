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


if __name__ == '__main__':


    file_path = "../other/validation_system/example_text.txt"

    with open(file_path, 'r') as f:

        for line in f:
            sentences_list = text_tokenizer.token_to_sentence(line)

            print("LINE: {}".format(sentences_list))


    # if "validation_system_input_file" not in settings:
    #     print("Need to define a file path under key 'validation_system_input_file' key that will be used for testing.")
    #     sys.exit()
    #
    # if "validation_system_output_files_location" not in settings:
    #     print("Need to define a file path under key 'validation_system_output_files_location' key that will be used for testing.")
    #     sys.exit()
    #
    # input_file_path = settings["validation_system_input_file"]
    # validation_files_location = settings["validation_system_output_files_location"]
    #
    # spellchecker_corrections_file_path = validation_files_location + "errors_text.txt"
    # errors_audit_log_file_path = validation_files_location + "errors_audit_log.txt"
    #
    # word_idx = 0
    #
    # with open(spellchecker_corrections_file_path, 'r') as corrections_file, open(errors_audit_log_file_path, 'r') as errors_audit_log:
    #     audit_log_file_tsv_reader = csv.reader(errors_audit_log, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     tsv_header = next(audit_log_file_tsv_reader)
    #     # audit_log_file_tsv.writerow(["Original Word", "Error Word", "Error Exists"])
    #
    #     for line in corrections_file:
    #         sentences_list = text_tokenizer.token_to_sentence(line)
    #
    #         for sentence in sentences_list:
    #
    #
    #
    #
    #     for line in input_file:
    #         output_line = ""
    #         for c in line:
    #             if c.isalnum() and randint(0, 100) < CHANGE_CHARACTER_PROBABILITY_PERCENTAGE:
    #                 characters_to_replace = create_error_from_character(c)
    #                 print("Changing {} to {}".format(c, characters_to_replace))
    #                 output_line += characters_to_replace
    #             else:
    #                 output_line += c
    #
    #         original_sentences_list = text_tokenizer.token_to_sentence(line)
    #         error_containing_sentences_list = text_tokenizer.token_to_sentence(output_line)
    #
    #         if len(original_sentences_list) != len(error_containing_sentences_list):
    #             print("Different number of sentences...")
    #             continue
    #
    #         for sentence_idx in range(0, len(original_sentences_list)):
    #             original_sentence_words = text_tokenizer.token_to_words(original_sentences_list[sentence_idx])
    #             error_sentence_words = text_tokenizer.token_to_words(error_containing_sentences_list[sentence_idx])
    #
    #             if len(original_sentence_words) != len(error_sentence_words):
    #                 print("Different number of words...")
    #                 continue
    #
    #             for word_idx in range(0, len(original_sentence_words)):
    #                 original_word = original_sentence_words[word_idx]
    #                 error_word = error_sentence_words[word_idx]
    #
    #                 audit_log_file_tsv.writerow([original_word, error_word, original_word != error_word])
    #                 # output_audit_log_file.write("Different: {}, Original: {}, Error: {}\n".format(original_word != error_word, original_word, error_word))
    #
    #         output_error_file.write(output_line)
    #
    #         print(line)
