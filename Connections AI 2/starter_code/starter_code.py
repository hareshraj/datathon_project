# starter_code.py
import numpy as np
from itertools import combinations
from gensim.models import KeyedVectors

word2vec_model = KeyedVectors.load_word2vec_format('/Users/haresh/gensim-data/word2vec-google-news-300/word2vec-google-news-300', binary=True)

def get_word2vec(): 
    return word2vec_model

def model(words, strikes, isOneAway, correctGroups, previousGuesses, error):
    """
    _______________________________________________________
    Parameters:
    words - 1D Array with 16 shuffled words
    strikes - Integer with number of strikes
    isOneAway - Boolean if your previous guess is one word away from the correct answer
    correctGroups - 2D Array with groups previously guessed correctly
    previousGuesses - 2D Array with previous guesses
    error - String with error message (0 if no error)

    Returns:
    guess - 1D Array with 4 words
    endTurn - Boolean if you want to end the puzzle
    _______________________________________________________
    """

    # Your Code here
    # Good Luck!
 
    if isinstance(words, str):
        words = np.array(eval(words))
    
    # Ensure every guess has exactly 4 words
    if error and "Please enter 4 words" in error:
        guess = list(words[:4])
        return guess, False

    # Check for and avoid duplicate guesses
    if error and "already guessed" in error:
        all_words = set(words)
        previous_words = set([word for guess in previousGuesses for word in guess])
        available_words = list(all_words - previous_words)
        if len(available_words) >= 4:
            guess = available_words[:4]
            return guess, False

    used_words = set([word for group in correctGroups for word in group])
    available_words = [word for word in words if word not in used_words]

    # Use Word2Vec to find similarities and group similar words
    def get_word_embedding(word):
        try:
            return word2vec_model[word]
        except KeyError:
            return np.zeros(word2vec_model.vector_size)

    word_vectors = np.array([get_word_embedding(word) for word in available_words])
    similarity_matrix = np.dot(word_vectors, word_vectors.T)

    # Find the most similar group of 4 words
    most_similar_group = None
    max_similarity = -np.inf

    for combination in combinations(range(len(available_words)), 4):
        similarity_score = sum(similarity_matrix[i, j] for i, j in combinations(combination, 2))
        if similarity_score > max_similarity:
            max_similarity = similarity_score
            most_similar_group = [available_words[i] for i in combination]

    if most_similar_group:
        return most_similar_group, False

    # If we have too many strikes or found most groups, consider ending
    if strikes >= 3 or len(correctGroups) >= 3:
        return [], True

    # If no similar group is found, make a reasonable guess with unused words
    if len(available_words) >= 4:
        guess = available_words[:4]
        return guess, False

    # If we can't make a good guess, end the turn
    return [], True
