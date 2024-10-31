import os
import random
import time

import openai
from dotenv import load_dotenv

load_dotenv()

model = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

board = None
player = 0
players = ["A", "B"]


def print_board(board):
    board_str = ""
    for i in range(9):
        if isinstance(board[i], int):
            board_str += " "
        else:
            board_str += board[i]

        if (i + 1) % 3 == 0:
            board_str += "\n"
        else:
            board_str += "|"

    print(board_str)


def did_player_win(player, board):
    winning_combinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]

    for combination in winning_combinations:
        if all(board[p] == player for p in combination):
            return True

    return False


def play(player, board):
    response = model.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are player {player}. Your job is to select a random open position from
                    a board with 9 possible positions. An open position is indicated with a number.
                    Never select a position that doesn't have a number. 
                """,
            },
            {
                "role": "assistant",
                "content": f"""
                Here is the initial board: {board}. 
                1. Select an open position (indicated by a number)
                2. Replace the number in the initial board with "{player}". Surround "{player}" with quotes.
                3. Return the following:

                Initial board is {board}
                Updated board: [UPDATED BOARD INCLUDING "{player}"]
                
                """,
            },
        ],
        temperature=0.1,
        top_p=0.1,
    )

    board_str = response.choices[0].message.content
    # print("Response:", board_str)
    board_str = board_str.split(":")[1].strip()
    board_str = board_str[:-1] if board_str[-1] == "." else board_str

    return eval(board_str)


def initialize():
    global board, player

    print("Starting a new game")

    board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    player = random.choice([0, 1])
    time.sleep(5)


initialize()

games = [0, 0]
while True:
    board = play(players[player], board)

    if board is None:
        print("This shouldn't have happened. Restarting the game.")
        initialize()
        continue

    print_board(board)

    if did_player_win(players[player], board):
        games[player] += 1
        print(f"Player {players[player]} wins. [A: {games[0]}, B: {games[1]}]")
        initialize()
        continue

    if all(p in players for p in board):
        print(f"Game is a draw. [A: {games[0]}, B: {games[1]}]")
        initialize()
        continue

    player = (player + 1) % 2
