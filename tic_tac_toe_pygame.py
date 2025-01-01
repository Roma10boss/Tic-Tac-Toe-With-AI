import pygame
import sys
import json
import os
import random
import math

# ==================================================
#              Q-LEARNING: LOAD TABLE
# ==================================================
Q_TABLE_FILE = "q_table.json"
Q = {}

def load_q_table(file_path):
    global Q
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            q_data = json.load(f)
        for state, actions in q_data.items():
            for action_str, value in actions.items():
                action = int(action_str)
                Q[(state, action)] = value
    else:
        print("[INFO] No Q-table file found. AI might play randomly!")
        Q = {}

def get_q_value(state, action):
    return Q.get((state, action), 0.0)

def choose_best_action(state):
    """Pick the best known action from Q, or random if unknown."""
    valid_actions = [i for i, ch in enumerate(state) if ch == ' ']
    if not valid_actions:
        return None
    qvals = [(get_q_value(state, a), a) for a in valid_actions]
    # If all Q=0 => random
    if all(qv[0] == 0.0 for qv in qvals):
        return random.choice(valid_actions)
    # Otherwise pick best
    return max(qvals, key=lambda x: x[0])[1]

# ==================================================
#              GAME LOGIC
# ==================================================
def check_winner(state, symbol):
    wins = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]
    for (a,b,c) in wins:
        if state[a] == state[b] == state[c] == symbol:
            return True
    return False

def is_draw(state):
    return ' ' not in state

# ==================================================
#              PYGAME SETUP
# ==================================================
pygame.init()
WINDOW_SIZE = 600
BOARD_SIZE = 480  # area for the 3x3 grid
TOP_MARGIN = (WINDOW_SIZE - BOARD_SIZE) // 2
LEFT_MARGIN = (WINDOW_SIZE - BOARD_SIZE) // 2

CELL_SIZE = BOARD_SIZE // 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
HOVER_GRAY = (150, 150, 150)

# We'll define a couple of gradients for a "modern" look
# Example: from teal-ish to navy-ish
GRADIENT_TOP = (65, 192, 200)   # teal
GRADIENT_BOTTOM = (24, 52, 105) # navy

X_COLOR = (240, 50, 50)
O_COLOR = (50, 120, 240)

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Modern Tic-Tac-Toe with Q-Learning AI")

# Fonts
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Verdana", 40, bold=True)
MOVE_FONT = pygame.font.SysFont("Verdana", 90, bold=True)
RESULT_FONT = pygame.font.SysFont("Verdana", 50, bold=True)
BTN_FONT = pygame.font.SysFont("Verdana", 25)

# Optional images for X, O
try:
    X_IMG = pygame.image.load("X.png")
    O_IMG = pygame.image.load("O.png")
    # Scale images
    X_IMG = pygame.transform.smoothscale(X_IMG, (CELL_SIZE, CELL_SIZE))
    O_IMG = pygame.transform.smoothscale(O_IMG, (CELL_SIZE, CELL_SIZE))
    USE_IMAGES = True
except:
    USE_IMAGES = False

clock = pygame.time.Clock()

# ==================================================
#         DRAWING FUNCTIONS FOR MODERN UI
# ==================================================
def draw_gradient_background(top_color, bottom_color, width, height):
    """
    Draw a vertical gradient from top_color to bottom_color.
    """
    # We'll draw horizontal lines from top to bottom, blending the color.
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

def draw_title_text():
    text_surf = TITLE_FONT.render("Tic-Tac-Toe", True, WHITE)
    text_rect = text_surf.get_rect(center=(WINDOW_SIZE//2, 40))
    screen.blit(text_surf, text_rect)

def draw_grid_lines():
    """Draw lines with a 'shadow' effect for a modern look."""
    line_thickness = 5

    # Add a faint shadow offset (2,2)
    shadow_color = (30, 30, 30, 60)  # partially transparent
    # We'll just draw black lines first offset by 2 px, to mimic a shadow

    # Vertical lines
    for c in range(1, 3):
        x = LEFT_MARGIN + c*CELL_SIZE
        # shadow
        pygame.draw.line(screen, shadow_color, (x+2, TOP_MARGIN+2), (x+2, TOP_MARGIN+BOARD_SIZE+2), line_thickness)
        # main line
        pygame.draw.line(screen, BLACK, (x, TOP_MARGIN), (x, TOP_MARGIN+BOARD_SIZE), line_thickness)

    # Horizontal lines
    for r in range(1, 3):
        y = TOP_MARGIN + r*CELL_SIZE
        # shadow
        pygame.draw.line(screen, shadow_color, (LEFT_MARGIN+2, y+2), (LEFT_MARGIN+BOARD_SIZE+2, y+2), line_thickness)
        # main line
        pygame.draw.line(screen, BLACK, (LEFT_MARGIN, y), (LEFT_MARGIN+BOARD_SIZE, y), line_thickness)

def draw_board(board_list):
    """
    Draw X or O with large font or images in each cell.
    """
    for i, cell in enumerate(board_list):
        row = i // 3
        col = i % 3
        x_pos = LEFT_MARGIN + col*CELL_SIZE
        y_pos = TOP_MARGIN + row*CELL_SIZE

        if cell == 'X':
            if USE_IMAGES:
                screen.blit(X_IMG, (x_pos, y_pos))
            else:
                text_surf = MOVE_FONT.render('X', True, X_COLOR)
                rect = text_surf.get_rect(center=(x_pos + CELL_SIZE//2, y_pos + CELL_SIZE//2))
                screen.blit(text_surf, rect)
        elif cell == 'O':
            if USE_IMAGES:
                screen.blit(O_IMG, (x_pos, y_pos))
            else:
                text_surf = MOVE_FONT.render('O', True, O_COLOR)
                rect = text_surf.get_rect(center=(x_pos + CELL_SIZE//2, y_pos + CELL_SIZE//2))
                screen.blit(text_surf, rect)

def get_cell_index(mx, my):
    if (mx < LEFT_MARGIN or mx > LEFT_MARGIN + BOARD_SIZE or
        my < TOP_MARGIN or my > TOP_MARGIN + BOARD_SIZE):
        return None
    col = (mx - LEFT_MARGIN) // CELL_SIZE
    row = (my - TOP_MARGIN) // CELL_SIZE
    return row*3 + col

# ---------------------------
#   ROUNDED RECT & BUTTONS
# ---------------------------
def draw_rounded_rect(surface, rect, color, radius=15):
    """
    Draw a "rounded rectangle" for a more modern "button" look.
    We can do this by using pygame's newer draw function or a custom approach.
    """
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_button(rect, text, base_color, hover_color, text_color=WHITE):
    """
    Draw a button with a hover effect. Return True if hovered, else False.
    """
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        color = hover_color
    else:
        color = base_color

    draw_rounded_rect(screen, rect, color, radius=12)
    # Center text
    text_surf = BTN_FONT.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    # Check for click
    mouse_click = pygame.mouse.get_pressed()
    if mouse_click[0] and rect.collidepoint(mouse_pos):
        return True
    return False

# Overlay for endgame (win/draw)
def draw_overlay(message):
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # black w/ alpha 150
    screen.blit(overlay, (0, 0))

    # Draw the message
    text_surf = RESULT_FONT.render(message, True, WHITE)
    text_rect = text_surf.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 60))
    screen.blit(text_surf, text_rect)

    # "New Game" button
    new_btn_rect = pygame.Rect(WINDOW_SIZE//2 - 120, WINDOW_SIZE//2, 100, 40)
    quit_btn_rect = pygame.Rect(WINDOW_SIZE//2 + 20, WINDOW_SIZE//2, 100, 40)

    new_clicked = draw_button(new_btn_rect, "New", (70,70,70), HOVER_GRAY)
    quit_clicked = draw_button(quit_btn_rect, "Exit", (70,70,70), HOVER_GRAY)

    return new_clicked, quit_clicked

# ==================================================
#               MAIN LOOP
# ==================================================
def main():
    load_q_table(Q_TABLE_FILE)

    board = [' '] * 9
    user_symbol = 'X'
    ai_symbol = 'O'
    current_symbol = 'X'  # X goes first

    running = True
    game_over = False
    result_message = ""

    while running:
        # 1) Draw a gradient background
        draw_gradient_background(GRADIENT_TOP, GRADIENT_BOTTOM, WINDOW_SIZE, WINDOW_SIZE)

        # 2) Title
        draw_title_text()

        # 3) Grid lines
        draw_grid_lines()

        # 4) Board
        draw_board(board)

        # 5) If game_over, show an overlay with "New" or "Exit"
        new_game_clicked = False
        quit_clicked = False
        if game_over:
            new_game_clicked, quit_clicked = draw_overlay(result_message)

        pygame.display.update()

        # 6) Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if not game_over:
                # If user clicks on board area
                if event.type == pygame.MOUSEBUTTONDOWN and current_symbol == user_symbol:
                    mx, my = pygame.mouse.get_pos()
                    idx = get_cell_index(mx, my)
                    if idx is not None and board[idx] == ' ':
                        board[idx] = user_symbol
                        # Check outcome
                        if check_winner(''.join(board), user_symbol):
                            result_message = "You Win!"
                            game_over = True
                        elif is_draw(''.join(board)):
                            result_message = "It's a Draw!"
                            game_over = True
                        else:
                            current_symbol = ai_symbol

        # 7) Handle AI turn
        if not game_over and current_symbol == ai_symbol:
            pygame.time.wait(500)
            state_str = ''.join(board)
            ai_move = choose_best_action(state_str)
            if ai_move is not None:
                board[ai_move] = ai_symbol
                if check_winner(''.join(board), ai_symbol):
                    result_message = "AI Wins!"
                    game_over = True
                elif is_draw(''.join(board)):
                    result_message = "It's a Draw!"
                    game_over = True
            else:
                result_message = "It's a Draw!"
                game_over = True
            current_symbol = user_symbol

        # 8) If game_over, check if user clicked "New" or "Exit"
        if game_over:
            if new_game_clicked:
                # Reset
                board = [' '] * 9
                current_symbol = 'X'
                result_message = ""
                game_over = False
            elif quit_clicked:
                running = False

        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
