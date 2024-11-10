import numpy as np
from itertools import combinations
from gensim.models import KeyedVectors

# Load the Word2Vec model
word2vec_model = KeyedVectors.load_word2vec_format('/Users/haresh/Downloads/td_submissions/connections_submission/gensim-data/word2vec-google-news-300/word2vec-google-news-300', binary=True)

def get_word2vec():
    return word2vec_model

# To store previous guesses and one-away information
previous_guesses_global = set()
last_guess = None
one_away_words = set()

def calculate_group_similarity(group):
    """Calculate how similar words are to each other using Word2Vec"""
    similarity_scores = []
    
    for word1, word2 in combinations(group, 2):
        try:
            # Get direct similarity between words
            similarity = word2vec_model.similarity(word1.lower(), word2.lower())
            similarity_scores.append(similarity)
        except KeyError:
            similarity_scores.append(0)
    
    # Return average similarity, heavily weighted
    return np.mean(similarity_scores) * 10 if similarity_scores else 0

def model(words, strikes, isOneAway, correctGroups, previousGuesses, error):
    """Model function for word grouping puzzle"""
    global previous_guesses_global, last_guess, one_away_words
    
    # Convert string representation to numpy array if needed
    if isinstance(words, str):
        words = np.array(eval(words))
    
    # Update one_away_words if last guess was one away
    if isOneAway and last_guess:
        one_away_words.update(last_guess)
    
    # Get available words (words not yet used in correct groups)
    used_words = set([word for group in correctGroups for word in group])
    available_words = [word for word in words if word not in used_words]
    
    # If we don't have enough available words, end the turn
    if len(available_words) < 4:
        return [], True
    
    # Find groups of words with high similarity
    potential_groups = []
    for combination in combinations(range(len(available_words)), 4):
        group = [available_words[i] for i in combination]
        
        # Skip if this group has been guessed before
        if tuple(sorted(group)) in previous_guesses_global:
            continue
        
        # Calculate similarity score for the group
        similarity_score = calculate_group_similarity(group)
        
        # Boost score if group contains words from a one-away guess
        one_away_overlap = len(set(group) & one_away_words)
        if one_away_overlap >= 2:
            similarity_score *= 1.5
        
        potential_groups.append((group, similarity_score))
    
    # Sort groups by similarity score
    potential_groups.sort(key=lambda x: x[1], reverse=True)
    
    # Return group with highest similarity if above threshold
    if potential_groups and potential_groups[0][1] > 0.3:
        best_group = potential_groups[0][0]
        previous_guesses_global.add(tuple(sorted(best_group)))
        last_guess = best_group if not isOneAway else None
        return best_group, False
    
    # If striked out or found all groups, end the turn
    if strikes >= 3 or len(correctGroups) >= 3:
        last_guess = None
        return [], True
    
    # If no valid guess, end the turn
    last_guess = None
    return [], True

def clear_previous_guesses():
    """Reset the previous guesses at the start of each puzzle"""
    global previous_guesses_global, last_guess, one_away_words
    previous_guesses_global = set()
    last_guess = None
    one_away_words = set()

clear_previous_guesses()