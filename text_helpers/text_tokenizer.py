import re
from cache.names import is_word_name


# TEXT_TO_SENTENCES_REGEX = '([\w\s]{0,})[^\w\s\\n]'
TEXT_TO_SENTENCES_REGEX = '([\w\s]{0,})([^\w\s\\n]{1})'
SENTENCE_TO_WORDS_REGEX = '([\w]{0,})'


def read_mk_dictionary(dictionary_path):
    dictionary_words = set()

    with open(dictionary_path, "r") as f:
        for line in f:
            dictionary_words.add(line.strip().lower())

    return dictionary_words


def read_file(input_file_path):

    text = ""

    with open(input_file_path, 'r') as input_file:

        for line in input_file:
            text += line.replace("\n", " ")

    return text


def token_to_sentence(text):
    """
    A function that from a given string (text) extracts sentences by using a Regex and returns a list of sentences.
    A sentence is defined as a continuous flow of words between 2 punctuation signs. Even though this is not a correct
    definition of a sentence, it's the best way if it is used in a language model.
    :param text: a string that we want to extract sentences from
    :return: a list of sentences
    """

    # add an extra dot for sentences that don't end with a punctuation sign
    text = text + "."

    regex_of_sentence = re.findall(TEXT_TO_SENTENCES_REGEX, text)
    print("Text={}, RegexOfSentences={}".format(text, regex_of_sentence))
    text_sentences = [(sentence.strip(), sign) for sentence, sign in regex_of_sentence]

    # remove last element if it's a sentence without a sign (to remove the extra dot if it's not needed)
    last_sentence_sign = text_sentences[-1]
    if last_sentence_sign[0] == "":
        text_sentences.pop()

    return text_sentences


# TODO: review usage. returns with capital letters now
def token_to_words(sentence):
    """
    A function that from a given sentence extracts a list of words using a regex and returns the list
    :param sentence: a string that represents 1 sentence
    :return: a list of words from the sentence
    """

    regex_of_word = re.findall(SENTENCE_TO_WORDS_REGEX, sentence)

    # words = [x.lower() for x in regex_of_word if x is not '']
    words = [x for x in regex_of_word if x is not '']

    return words


def is_special_word(word):

    return is_word_name(word) or word.isdigit()
