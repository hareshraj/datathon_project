import numpy as np
from itertools import combinations
from gensim.models import KeyedVectors

# Load the Word2Vec model
word2vec_model = KeyedVectors.load_word2vec_format('/Users/haresh/gensim-data/word2vec-google-news-300/word2vec-google-news-300', binary=True)

def get_word2vec():
    return word2vec_model

# To store previous guesses for each puzzle
previous_guesses_global = set()

def model(words, strikes, isOneAway, correctGroups, previousGuesses, error):
    """
    Model function for word grouping puzzle
    """
    global previous_guesses_global
    
    # Convert string representation to numpy array if needed
    if isinstance(words, str):
        words = np.array(eval(words))
    
    # Get available words (words not yet used in correct groups)
    used_words = set([word for group in correctGroups for word in group])
    available_words = [word for word in words if word not in used_words]
    
    # If we don't have enough available words, end the turn
    if len(available_words) < 4:
        return [], True
    
    # Use Word2Vec to find similarities and group similar words
    def get_word_embedding(word):
        try:
            return word2vec_model[word]
        except KeyError:
            return np.zeros(word2vec_model.vector_size)

    word_vectors = np.array([get_word_embedding(word) for word in available_words])
    similarity_matrix = np.dot(word_vectors, word_vectors.T)

    # Find the most similar group of 4 words that hasn't been guessed before
    potential_groups = []
    for combination in combinations(range(len(available_words)), 4):
        group = [available_words[i] for i in combination]
        # Check if this group has been guessed before
        if tuple(sorted(group)) not in previous_guesses_global:
            similarity_score = sum(similarity_matrix[i, j] for i, j in combinations(combination, 2))
            potential_groups.append((group, similarity_score))
    
    # Sort groups by similarity score
    potential_groups.sort(key=lambda x: x[1], reverse=True)
    
    # If we have any valid groups, return the most similar one
    if potential_groups:
        best_group = potential_groups[0][0]
        previous_guesses_global.add(tuple(sorted(best_group)))
        return best_group, False
    
    # If we have too many strikes or found most groups, end the turn
    if strikes >= 3 or len(correctGroups) >= 3:
        return [], True
    
    # If we somehow can't make a valid guess, end the turn
    return [], True

def clear_previous_guesses():
    """Reset the previous guesses at the start of each puzzle"""
    global previous_guesses_global
    previous_guesses_global = set()

# Ensure the clear function is called at the start of a new puzzle
clear_previous_guesses()
