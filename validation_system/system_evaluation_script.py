from configuration import settings
import sys
from text_helpers import text_tokenizer
import csv
import json


def read_errors_audit_log(errors_audit_file_path):

    words_list = list()

    with open(errors_audit_file_path, 'r') as errors_audit_file:
        audit_log_file_tsv_reader = csv.DictReader(errors_audit_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for word_comb in audit_log_file_tsv_reader:
            words_list.append(word_comb)

    return words_list


def load_spellchecker_output(spellchecker_output_file_path):

    with open(spellchecker_output_file_path, 'r') as json_file:
        return json.load(json_file)


if __name__ == '__main__':

    if "validation_system_files_directory" not in settings:
        print("Need to define a file path under key 'validation_system_files_directory' key that will be used for testing.")
        sys.exit()

    if "validation_system_input_file_name" not in settings:
        print("Need to define a file path under key 'validation_system_input_file_name' key that will be used for testing.")
        sys.exit()

    validation_system_files_directory = settings["validation_system_files_directory"]

    spellchecker_output_file_path = validation_system_files_directory + "spellchecker_output.json"
    errors_audit_log_file_path = validation_system_files_directory + "errors_audit_log.txt"

    # corrected_text = text_tokenizer.read_file(correction_file_path)
    spellchecker_output = load_spellchecker_output(spellchecker_output_file_path)
    audit_log_records = read_errors_audit_log(errors_audit_log_file_path)

    word_idx = 0

    total_errors = 0
    first_correction = 0
    all_corrections = 0

    for word_suggestion in spellchecker_output:

        word = word_suggestion["Збор"]

        if not word.isalnum():
            continue

        audit_log_word_combination = audit_log_records[word_idx]
        word_idx += 1

        # print("OriginalWord={}, ErrorWord={}, SpellcheckerWord={}".format(audit_log_word_combination["Word"], audit_log_word_combination["ErrorWord"], word))

        if audit_log_word_combination["ErrorAdded"] == 'False':
            continue

        original_word = audit_log_word_combination["Word"].lower()

        total_errors += 1

        suggestions = list()

        if "Предлози" in word_suggestion:
            suggestions = word_suggestion["Предлози"]

        correction_found = False
        first_correction_found = False

        for suggestion in suggestions:

            is_suggestion_equal = suggestion.lower() == original_word

            if not first_correction_found and is_suggestion_equal:
                first_correction += 1

            first_correction_found = True

            if is_suggestion_equal:
                all_corrections += 1
                correction_found = True
                break

        if not correction_found:
            print("OriginalWord={}, ErrorWord={}, SpellcheckerWord={}".format(audit_log_word_combination["Word"],
                                                                              audit_log_word_combination["ErrorWord"],
                                                                              word))

    print("Words={}".format(word_idx))
    print("TotalErrors={}".format(total_errors))
    print("First Suggestion Correct={}, First Suggestion Correct Percentage".format(first_correction, (first_correction / total_errors) * 100))
    print("All Suggestions Correct={}, All Suggestions Correct Percentage".format(all_corrections, (all_corrections / total_errors) * 100))


    # word_idx = 0
    #
    # errors_count = 0
    # errors_corrected_count = 0
    # errors_not_corrected_count = 0
    #
    # correct_words_count = 0
    # correct_words_unchanged_count = 0
    # correct_words_mistaken_count = 0
    #
    # for sentence in sentences:
    #
    #     words_list = text_tokenizer.token_to_words(sentence)
    #
    #     for word in words_list:
    #
    #         audit_log_record = audit_log_records[word_idx]
    #         word_idx = word_idx + 1
    #
    #         if audit_log_record["ErrorAdded"] == "True":
    #             # print("Error found")
    #             errors_count = errors_count + 1
    #
    #             if word.lower() == audit_log_record["Word"]:
    #                 errors_corrected_count = errors_corrected_count + 1
    #             else:
    #                 errors_not_corrected_count = errors_not_corrected_count + 1
    #         else:
    #             # print("Correct word found")
    #
    #             correct_words_count = correct_words_count + 1
    #
    #             if word.lower() == audit_log_record["Word"]:
    #                 correct_words_unchanged_count = correct_words_unchanged_count + 1
    #             else:
    #                 print("Sentence={}, OriginalWord={}, CorrectedWord={}, Message= Correct word mistaken".format(sentence, audit_log_record["Word"], word.lower()))
    #                 correct_words_mistaken_count = correct_words_mistaken_count + 1

    # print("Errors={}, CorrectWords={}".format(errors_count, correct_words_count))
    #
    # total_words_count = correct_words_count + errors_count
    # error_percentage = errors_count / total_words_count
    #
    # errors_corrected_percentage = errors_corrected_count / errors_count
    # errors_remaining_percentage = errors_not_corrected_count / errors_count
    #
    # correct_words_unchanged_percentage = correct_words_unchanged_count / correct_words_count
    # correct_words_mistaken_percentage = correct_words_mistaken_count / correct_words_count
    #
    # total_words_correctness_percentage = (errors_corrected_count + correct_words_unchanged_count) / total_words_count
    #
    # print("Report")
    # print("Total Words: {}".format(total_words_count))
    #
    # print("\nCorrect Words")
    # print("Total Correct Words Count: {}".format(correct_words_count))
    # print("Correct Words Unchanged Count: {}".format(correct_words_unchanged_count))
    # print("Correct Words Mistaken Count: {}".format(correct_words_mistaken_count))
    #
    # print("\nErrors")
    # print("Total Errors: {}".format(errors_count))
    # print("Errors Corrected: {}".format(errors_corrected_count))
    # print("Errors Not Corrected: {}".format(errors_not_corrected_count))
    #
    # print("TotalWords={}, Errors={}, CorrectWords={}, ErrorPercentage={}, CorrectedErrorsPercent={}, "
    #       "UncorrectedErrorsPercent={}, CorrectWordsUnchangedPercent={}, CorrectWordsMistakenPercent={}, TotalCorrectnessPercent={}"
    #       .format(total_words_count, errors_count, correct_words_count, error_percentage, errors_corrected_percentage,
    #               errors_remaining_percentage, correct_words_unchanged_percentage, correct_words_mistaken_percentage, total_words_correctness_percentage))
