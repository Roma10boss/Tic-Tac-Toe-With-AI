import random
import json
import os

# Hyperparameters
ALPHA = 0.5     # Learning rate
GAMMA = 0.9     # Discount factor
EPSILON_START = 1.0   # Initial exploration rate
EPSILON_END = 0.01    # Final exploration rate
EPISODES = 20000      # Number of self-play games

REWARD_WIN = 1.0
REWARD_LOSE = -1.0
REWARD_DRAW = 0.0

SAVE_FILE = "q_table.json"

# Q-table: dict((state, action) -> q_value)
Q = {}

def save_q_table(file_path=SAVE_FILE):
    """Save the Q dictionary to a JSON file."""
    with open(file_path, "w") as f:
        # We can't directly dump a dict with tuple keys, so we transform
        q_data = {}
        for (state, action), value in Q.items():
            # state is a string, action is an int
            # we'll store them as strings
            if state not in q_data:
                q_data[state] = {}
            q_data[state][str(action)] = value
        json.dump(q_data, f)

def load_q_table(file_path=SAVE_FILE):
    """Load Q dictionary from a JSON file if it exists."""
    global Q
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            q_data = json.load(f)
        # Convert the action keys back to int
        for state, actions in q_data.items():
            for action_str, value in actions.items():
                action = int(action_str)
                Q[(state, action)] = value
    else:
        Q = {}

# ---------------------------
#  TIC-TAC-TOE GAME LOGIC
# ---------------------------
def initial_state():
    """Return an empty 9-char board for new game."""
    return "         "  # 9 spaces

def available_actions(state_str):
    """Return a list of valid move indices (0..8) where state_str is blank."""
    return [i for i, ch in enumerate(state_str) if ch == ' ']

def next_state(state_str, action, symbol):
    """
    Return the new state string after 'symbol' ('X'/'O') 
    plays in position 'action' (0..8).
    """
    lst = list(state_str)
    lst[action] = symbol
    return "".join(lst)

def check_winner(state_str, symbol):
    """Return True if symbol has won in the given state_str."""
    wins = [
        (0,1,2), (3,4,5), (6,7,8),  # rows
        (0,3,6), (1,4,7), (2,5,8),  # cols
        (0,4,8), (2,4,6)            # diagonals
    ]
    for (a,b,c) in wins:
        if state_str[a] == state_str[b] == state_str[c] == symbol:
            return True
    return False

def is_draw(state_str):
    """Return True if board is full and no winner."""
    return ' ' not in state_str

# ---------------------------
#  Q-LEARNING SUPPORT
# ---------------------------
def get_q_value(state, action):
    """Return the Q-value for (state, action) or 0.0 if not in Q."""
    return Q.get((state, action), 0.0)

def best_action(state):
    """Return the action with the highest Q-value for this state."""
    acts = available_actions(state)
    if not acts:
        return None
    # sort by Q-value descending
    best = max(acts, key=lambda a: get_q_value(state, a))
    return best

def epsilon_greedy_action(state, epsilon):
    """Return an action using epsilon-greedy strategy."""
    acts = available_actions(state)
    if not acts:
        return None
    if random.random() < epsilon:
        return random.choice(acts)  # explore
    else:
        return best_action(state)   # exploit

def update_q_value(old_state, action, reward, new_state):
    """Apply the Q-learning update rule."""
    old_q = get_q_value(old_state, action)
    max_q_next = 0.0
    next_acts = available_actions(new_state)
    if next_acts:
        max_q_next = max(get_q_value(new_state, a) for a in next_acts)
    new_q = old_q + ALPHA * (reward + GAMMA * max_q_next - old_q)
    Q[(old_state, action)] = new_q

def play_one_game(epsilon):
    """
    Play one game of Tic-Tac-Toe (X vs O) using epsilon-greedy for both.
    Returns +1 if X wins, -1 if O wins, 0 if draw.
    """
    state = initial_state()
    current_symbol = 'X'
    other_symbol = 'O'

    # Track the last state/action for X and O to update Q
    last_state = {'X': None, 'O': None}
    last_action = {'X': None, 'O': None}

    while True:
        # current player picks an action
        action = epsilon_greedy_action(state, epsilon)
        if action is None:
            # no moves left => draw
            # update last move with draw reward if needed
            return 0

        # store old state/action for updating
        old_state = state
        old_action = action

        # move
        state = next_state(state, action, current_symbol)

        # if we want to do small step updates for each move:
        if last_state[current_symbol] is not None:
            # update with an intermediate reward of 0
            update_q_value(last_state[current_symbol],
                           last_action[current_symbol],
                           0.0,
                           old_state)

        # check if current player won
        if check_winner(state, current_symbol):
            # reward this final move
            update_q_value(old_state, action, REWARD_WIN, state)
            # punish the opponent's last move (if any)
            opp = other_symbol
            if last_state[opp] is not None:
                update_q_value(last_state[opp],
                               last_action[opp],
                               REWARD_LOSE,
                               old_state)
            return +1 if current_symbol == 'X' else -1

        # check for draw
        if is_draw(state):
            # reward final move with 0
            update_q_value(old_state, action, REWARD_DRAW, state)
            return 0

        # switch player
        last_state[current_symbol] = old_state
        last_action[current_symbol] = old_action
        current_symbol, other_symbol = other_symbol, current_symbol


def main():
    load_q_table(SAVE_FILE)

    epsilon = EPSILON_START
    # We will do an exponential decay from EPSILON_START to EPSILON_END
    if EPSILON_START > 0:
        decay = (EPSILON_END / EPSILON_START) ** (1.0 / EPISODES)
    else:
        decay = 1.0

    x_wins = 0
    o_wins = 0
    draws = 0

    for episode in range(EPISODES):
        result = play_one_game(epsilon)
        if result == +1:
            x_wins += 1
        elif result == -1:
            o_wins += 1
        else:
            draws += 1

        # Decay epsilon
        epsilon = max(EPSILON_END, epsilon * decay)

    print(f"Training completed after {EPISODES} games.")
    print(f"X wins: {x_wins}, O wins: {o_wins}, Draws: {draws}, epsilon={epsilon:.4f}")

    # Save Q-table
    save_q_table(SAVE_FILE)
    print("Q-table saved.")

if __name__ == "__main__":
    main()
