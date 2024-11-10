# evaluator.py

import random
import numpy as np
import requests
import json

def evalFunction():
    puzzles = load_puzzles()
    totalPoints = 0

    for z, puzzle in enumerate(puzzles, start=1):
        clear_previous_guesses()  # Reset guesses at the start of each puzzle
        shuffledPuzzle = shufflePuzzles(puzzle)
        strikes, correctGroups, previousGuesses, error, isOneAway = 0, [], [], 0, False
        invalidGuesses = 0
        pointsForPuzzle = 0  # Track points for each puzzle

        while strikes < 4 and len(correctGroups) < 4 and invalidGuesses < 7:
            data = {
                "words": shuffledPuzzle,
                "strikes": strikes,
                "isOneAway": isOneAway,
                "correctGroups": correctGroups,
                "previousGuesses": previousGuesses,
                "error": error
            }

            r = requests.post("http://127.0.0.1:5000", json=data)
            participantGuess = r.json()['guess']
            endTurn = r.json()['endTurn']
            print("Participant guess:", participantGuess)

            # Validate guess length
            if len(participantGuess) != 4:
                error = "Please enter 4 words."
                invalidGuesses += 1
                print("Invalid guess length:", participantGuess)
                continue

            # Check for duplicates
            if sorted(participantGuess) in [sorted(g) for g in previousGuesses]:
                error = "You have already guessed this combination."
                invalidGuesses += 1
                print("Duplicate guess:", participantGuess)
                continue
            else:
                error = 0
                previousGuesses.append(participantGuess)

            if endTurn:
                break

            correctlyGuessed = False
            for group in puzzle:
                if set(group) == set(participantGuess):
                    correctlyGuessed = True
                    correctGroups.append(group)
                    pointsForPuzzle += 1  # Increment points for a correct guess
                    break
                elif len(set(group).symmetric_difference(set(participantGuess))) == 2:
                    isOneAway = True
                    print("One away")
                    break
                else:
                    isOneAway = False

            if not correctlyGuessed:
                strikes += 1
                print(f"Strike added. Total strikes: {strikes}")

        log_game(z, previousGuesses, correctGroups, strikes)
        totalPoints += pointsForPuzzle  # Add puzzle points to the total
        print(f"Total points scored by model on puzzle {z}: {pointsForPuzzle}")

    print(f"Overall total points scored by model: {totalPoints}")

def clear_previous_guesses():
    global previous_guesses_global
    previous_guesses_global = set()


def load_puzzles():
    with open('sample_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Create a 3D array (X puzzles, 4 rows, 4 words)
    puzzles_3d = []

    for puzzle in data:
        # Extract the answers for each puzzle
        puzzle_groups = puzzle["answers"]
        # Extract only the words from each group
        puzzle_words = [group["words"] for group in puzzle_groups]
        puzzles_3d.append(puzzle_words)

    return puzzles_3d

def shufflePuzzles(puzzle):
	# Return puzzle shuffled as a 1d array
	flattenedPuzzle = np.array(puzzle).reshape(-1)
	np.random.shuffle(flattenedPuzzle)
	return np.array2string(flattenedPuzzle, separator=', ')

import json

def log_game(puzzle_id, guesses, correct_groups, strikes):
    log_entry = {
        "puzzle_id": puzzle_id,
        "guesses": guesses,
        "correct_groups": correct_groups,
        "strikes": strikes
    }
    with open('log_data.json', 'a') as f:
        json.dump(log_entry, f)
        f.write("\n")

evalFunction()
