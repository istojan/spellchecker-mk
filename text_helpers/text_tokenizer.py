import re


TEXT_TO_SENTENCES_REGEX = '([\w\s]{0,})[^\w\s]'
SENTENCE_TO_WORDS_REGEX = '([\w]{0,})'


def read_mk_dictionary(dictionary_path):
    dictionary_words = set()

    with open(dictionary_path, "r") as f:
        for line in f:
            dictionary_words.add(line.strip().lower())

    return dictionary_words


def token_to_sentence(text):
    """
    A function that from a given string (text) extracts sentences by using a Regex and returns a list of sentences.
    A sentence is defined as a continuous flow of words between 2 punctuation signs. Even though this is not a correct
    definition of a sentence, it's the best way if it is used in a language model.
    :param text: a string that we want to extract sentences from
    :return: a list of sentences
    """

    regex_of_sentence = re.findall(TEXT_TO_SENTENCES_REGEX, text)
    text_sentences = [x.strip() for x in regex_of_sentence if x is not '']

    print("Text={}, Sentences={}, Extracted sentences".format(text, text_sentences))

    return text_sentences


def token_to_words(sentence):
    """
    A function that from a given sentence extracts a list of words using a regex and returns the list
    :param sentence: a string that represents 1 sentence
    :return: a list of words from the sentence
    """

    regex_of_word = re.findall(SENTENCE_TO_WORDS_REGEX, sentence)

    words = [x.lower() for x in regex_of_word if x is not '']

    return words
