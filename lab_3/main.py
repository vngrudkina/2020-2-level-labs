"""
Language detection using n-grams
"""

import re
import math
# 4
def tokenize_by_sentence(text: str) -> tuple:
    """
    Splits a text into sentences, sentences into tokens, tokens into letters
    Tokens are framed with '_'
    :param text: a text
    :return: a tuple of sentence with tuples of tokens split into letters
    e.g.
    text = 'She is happy. He is happy.'
    -->  (
         (('_', 's', 'h', 'e', '_'), ('_', 'i', 's', '_'), ('_', 'h', 'a', 'p', 'p', 'y', '_')),
         (('_', 'h', 'e', '_'), ('_', 'i', 's', '_'), ('_', 'h', 'a', 'p', 'p', 'y', '_'))
         )
    """
    if not isinstance(text, str):
        return ()
    tokens = []
    sentences = text.split('.')
    for sentence in sentences:
        letters = []
        list_of_tokens = re.sub('[^a-z \n]', '', sentence.lower()).split()
        for token in list_of_tokens:
            letters.append(tuple(['_'] + list(token) + ['_']))
        if letters:
            tokens.append(tuple(letters))
    return tuple(tokens)



# 4
class LetterStorage:

    def __init__(self):
        self.storage = {}

    def _put_letter(self, letter: str) -> int:
        """
        Puts a letter into storage, assigns a unique id
        :param letter: a letter
        :return: 0 if succeeds, 1 if not
        """

        if not isinstance(letter, str) or not letter:
            return 1
        if letter not in self.storage:
            self.storage[letter] = len(self.storage) + 1
        return 0

    def get_id_by_letter(self, letter: str) -> int:
        """
        Gets a unique id by a letter
        :param letter: a letter
        :return: an id
        """

        if not isinstance(letter, str) or not letter or letter not in self.storage:
            return -1
        return self.storage[letter]

    def update(self, corpus: tuple) -> int:
        """
        Fills a storage by letters from the corpus
        :param corpus: a tuple of sentences
        :return: 0 if succeeds, 1 if not
        """
        if not isinstance(corpus, tuple):
            return 1
        for sentence in corpus:
            for token in sentence:
                for letter in token:
                    self._put_letter(letter)
        return 0


# 6
def encode_corpus(storage: LetterStorage, corpus: tuple) -> tuple:
    """
    Encodes sentences by replacing letters with their ids
    :param storage: an instance of the LetterStorage class
    :param corpus: a tuple of sentences
    :return: a tuple of the encoded sentences
    """
    if not isinstance(storage, LetterStorage) or not isinstance(corpus, tuple):
        return()
    encoded_corpus = []
    for sentence in corpus:
        encoded_sentence = []
        for token in sentence:
            encoded_token = []
            for letter in token:
                encoded_token.append(storage.get_id_by_letter(letter))
            encoded_sentence.append(tuple(encoded_token))
        encoded_corpus.append(tuple(encoded_sentence))
    return tuple(encoded_corpus)



# 6
class NGramTrie:

    def __init__(self, n: int):
        self.size = n
        self.n_grams = ()
        self.n_gram_frequencies = {}
        self.n_gram_log_probabilities = {}

    def fill_n_grams(self, encoded_text: tuple) -> int:
        """
        Extracts n-grams from the given sentence, fills the field n_grams
        :return: 0 if succeeds, 1 if not
        """
        if not isinstance(encoded_text, tuple):
            return 1
        result = []
        for sentence in encoded_text:
            sentence_gram = []
            for token in sentence:
                token_gram = []
                for index in range(len(token) - self.size + 1):
                    token_gram.append(tuple(token[index:index + self.size]))
                sentence_gram.append(tuple(token_gram))
            result.append(tuple(sentence_gram))
        self.n_grams = tuple(result)
        return 0

    def calculate_n_grams_frequencies(self) -> int:
        """
        Fills in the n-gram storage from a sentence, fills the field n_gram_frequencies
        :return: 0 if succeeds, 1 if not
        """
        if not self.n_grams:
            return 1
        for sentence in self.n_grams:
            for word in sentence:
                for n_gram in word:
                    self.n_gram_frequencies[n_gram] = self.n_gram_frequencies.get(n_gram, 0) + 1
        return 0

    def calculate_log_probabilities(self) -> int:
        """
        Gets log-probabilities of n-grams, fills the field n_gram_log_probabilities
        :return: 0 if succeeds, 1 if not
        """
        if not self.n_gram_frequencies:
            return 1
        for n_gram, frequency in self.n_gram_frequencies.items():
            total_n_grams_number = 0
            for n_gram1 in self.n_gram_frequencies:
                if n_gram1[:-1] == n_gram[:-1]:
                    total_n_grams_number += self.n_gram_frequencies[n_gram1]
            probability = frequency / total_n_grams_number
            self.n_gram_log_probabilities[n_gram] = math.log(probability)
        return 0


    def top_n_grams(self, k: int) -> tuple:
        """
        Gets k most common n-grams
        :return: a tuple with k most common n-grams
        """
        if not isinstance(k, int) or k < 0 or not self.n_gram_frequencies:
            return ()
        return tuple(sorted(self.n_gram_frequencies, key=self.n_gram_frequencies.get, reverse=True)[:k])

# 8
class LanguageDetector:

    def __init__(self, trie_levels: tuple = (2,), top_k: int = 10):
        self.trie_levels = trie_levels
        self.top_k = top_k
        self.n_gram_storages = {}

    def new_language(self, encoded_text: tuple, language_name: str) -> int:
        """
        Fills NGramTries with regard to the trie_levels field
        :param encoded_text: an encoded text
        :param language_name: a language
        :return: 0 if succeeds, 1 if not
        """
        if (not isinstance(encoded_text, tuple) or not all(isinstance(element, tuple) for element in encoded_text)
                or not isinstance(language_name, str)):
            return 1

        self.n_gram_storages[language_name] = {}
        for element in self.trie_levels:
            new_language = NGramTrie(element)
            new_language.fill_n_grams(encoded_text)
            new_language.calculate_n_grams_frequencies()
            new_language.calculate_log_probabilities()
            self.n_gram_storages[language_name][element] = new_language
        return 0

    @staticmethod
    def _calculate_distance(first_n_grams: tuple, second_n_grams: tuple) -> int:
        """
        Calculates distance between top_k n-grams
        :param first_n_grams: a tuple of the top_k n-grams
        :param second_n_grams: a tuple of the top_k n-grams
        :return: a distance
        """
        if ((isinstance(first_n_grams, tuple) and not first_n_grams) or
                (isinstance(second_n_grams, tuple) and not second_n_grams)):
            return 0
        if (not isinstance(first_n_grams, tuple) or not isinstance(second_n_grams, tuple)
                or not all(isinstance(i, tuple) for i in first_n_grams)
                or not all(isinstance(i, tuple) for i in second_n_grams)):
            return -1
        distance = 0
        for element, n_gram in enumerate(first_n_grams):
            if n_gram in second_n_grams:
                distance += abs(second_n_grams.index(n_gram) - element)
            else:
                distance += len(second_n_grams)
        return distance

    def detect_language(self, encoded_text: tuple) -> dict:
        """
        Detects the language the unknown text is written in using the function _calculate_distance
        :param encoded_text: a tuple of sentences with tuples of tokens split into letters
        :return: a dictionary where a key is a language, a value – the distance
        """
        if not isinstance(encoded_text, tuple) or not all(isinstance(element, tuple) for element in encoded_text):
            return {}
        language_distance_dict = {}
        for language, dictionary in self.n_gram_storages.items():
            distances = 0
            for n_gram_size, n_gram_trie in dictionary.items():
                top_n_grams = n_gram_trie.top_n_grams(self.top_k)
                unknown_n_gram_trie = NGramTrie(n_gram_size)
                unknown_n_gram_trie.fill_n_grams(encoded_text)
                unknown_n_gram_trie.calculate_n_grams_frequencies()
                unknown_top_n_grams= unknown_n_gram_trie.top_n_grams(self.top_k)
                distances += self._calculate_distance(top_n_grams, unknown_top_n_grams)
            language_distance_dict[language] = distances / len(dictionary)
        return language_distance_dict

# 10
class ProbabilityLanguageDetector(LanguageDetector):

    @staticmethod
    def _calculate_sentence_probability(n_gram_storage: NGramTrie, sentence_n_grams: tuple) -> float:
        """
        Calculates sentence probability
        :param n_gram_storage: a filled NGramTrie with log-probabilities
        :param sentence_n_grams: n-grams from a sentence
        :return: a probability of a sentence
        """
        pass

    def detect_language(self, encoded_text: tuple) -> dict:
        """
        Detects the language the unknown sentence is written in using sentence probability in different languages
        :param encoded_text: a tuple of sentences with tuple s of tokens split into letters
        :return: a dictionary with language_name: probability
        """
        pass
