from configuration import settings

NAMES_SET = set()


def initialize_names_cache():

    if "male_names_file_path" not in settings:
        print("Key=\"male_names_file_path\", Message=\"No key for male names file path defined in configuration file.\"")
    else:
        with open(settings["male_names_file_path"], "r") as f1:
            for name in f1:
                NAMES_SET.add(name.strip().lower())

    if "female_names_file_path" not in settings:
        print("Key=\"female_names_file_path\", Message=\"No key for female names file path defined in configuration file.\"")
    else:
        with open(settings["female_names_file_path"], "r") as f1:
            for name in f1:
                NAMES_SET.add(name.strip().lower())


def is_word_name(word):
    return word.lower() in NAMES_SET
