# Tic-Tac-Toe-With-AI

# Project Overview

This repository contains a **modern, visually appealing Tic-Tac-Toe game** that integrates a **Q-learning AI**. The AI has been **extensively trained** through a high volume of **self-play** to learn optimal (or near-optimal) strategies. By storing its learned Q-values in a **Q-table**, the AI can efficiently retrieve the best moves during user gameplay.

A **Pygame GUI** presents the board with a **gradient background**, **shadowed grid lines**, **rounded-rectangle buttons**, and **semi-transparent overlays** to announce game outcomes (win, lose, or draw). These features combine to deliver a polished, engaging experience for both casual players and recruiters interested in your technical and design expertise.

---

## Detailed Features

### Q-Learning AI

- A dedicated script, `train_tic_tac_toe.py`, conducts **thousands of self-play matches**, progressively refining the AI’s Q-values.  
- The final **Q-table** is saved as `q_table.json`, ensuring that subsequent runs of the game utilize previously learned strategies.  
- During gameplay, the AI consults these Q-values, aiming to block the user and force draws or secure a win when possible.

### Modern Pygame User Interface

- **Gradient Background**: The main window uses a smooth color gradient, adding depth and visual appeal.  
- **Shadowed Grid Lines**: Subtle drop shadows give a professional, modern look.  
- **Rounded-Rectangle Buttons**: In the overlay, “New Game” and “Exit” buttons appear with hover and click effects.  
- **Semi-Transparent Overlays**: End-of-game messages (win/draw) display on a dimmed screen, ensuring the result is clear.

### Engaging Gameplay Elements

- **User vs. AI**: You place an **X** on your turn, and the AI responds with **O** shortly thereafter.  
- **Multiple Outcomes**: Enjoy dynamic feedback—if the user or AI wins, a corresponding message is displayed. If the board is filled, it’s a **draw**.  
- **Post-Game Options**: At the conclusion of each match, choose **“New Game”** to reset the board immediately, or **“Exit”** to close the window.

### Optional Customization

- **Visual Assets**: Swap out `X.png` and `O.png` for your own images or icons.  
- **Color and Style**: Tweak gradients, fonts, grid line thickness, and button shapes in `tic_tac_toe_modern.py`.  
- **Board Dimensions**: Adjust `WINDOW_SIZE` or `BOARD_SIZE` for smaller or larger game areas.
