# Blocky Game Project [March 2024]

Welcome to the Blocky Game Project! This repository hosts the code for **Blocky**, a grid-based, turn-based strategy game. Blocky challenges players to manipulate a colorful game board in a bid to reach specific goals and score as highly as possible.

In Blocky, each player works on a unique goal: creating the largest "blob" of a color or maximizing the number of units of a particular color around the board's perimeter. Players can rotate, smash, paint, and combine blocks to achieve their objectives, making it both a creative and strategic game.

---

## Game Overview

The Blocky game board is made up of colored blocks, which are structured hierarchically in a tree format. Each block can either be a solid color or be subdivided into four equal-sized blocks, creating a complex structure that players can manipulate through various actions.

The game can be played solo or with multiple players, including human and computer-controlled opponents. There are three types of players:
- **Human Player**: Makes moves based on user input.
- **Random Player**: Chooses moves randomly.
- **Smart Player**: Selects moves based on score maximization.

The player with the highest score after a predetermined number of turns wins the game.

## Key Features

### Actions and Moves
Players can perform a variety of actions, each affecting the board differently:
- **Rotate**: Rotate a block 90° clockwise or counterclockwise.
- **Swap**: Swap the left and right or top and bottom halves of a block.
- **Smash**: Subdivide a block into four new blocks of random colors.
- **Paint**: Change the color of a single block.
- **Combine**: Merge the colors of child blocks into a single parent block.
- **Pass**: Skip a turn without making any moves.

### Goals and Scoring
Each player is assigned a goal at the beginning of the game, which determines their objective:
- **Blob Goal**: Create the largest connected “blob” of a target color.
- **Perimeter Goal**: Place the target color around the board’s perimeter, with corner cells offering extra points.

In addition to scoring points based on goals, actions like smashing, painting, and combining carry point penalties, making it important for players to strategize their moves.

### Customizable Game Settings
Configure your Blocky game experience with various settings:
- **Board Depth**: Control the maximum depth of recursive subdivisions.
- **Player Types and Count**: Play with human, random, or smart players.
- **Turn Limit**: Set the number of moves per game.

## Project Structure

- **actions.py**: Defines the available moves and actions.
- **block.py**: Implements the Block structure, representing the hierarchical game board.
- **game.py**: Coordinates game setup and flow.
- **goal.py**: Defines scoring goals and scoring logic.
- **player.py**: Implements the different types of players.
- **renderer.py**: Handles the visual representation of the game board.
- **state.py**: Manages the game state.
- **images/**: Stores example images and diagrams.

## Getting Started

To get started, clone this repository and navigate to the project folder. Run `game.py` to launch the game. Make sure you have Python 3.7 or higher installed.

```bash
git clone https://github.com/username/Blocky.git
cd Blocky
python3 game.py
```

### Controls

- **W/S**: Increase/decrease selection level on the board.
- **Keyboard shortcuts**: Use displayed instructions to perform actions like rotating, smashing, and painting blocks.

### Adding Players
To modify the player setup, edit `game.py` and choose the desired configuration of human, random, or smart players.

---

## Development Roadmap

- **Feature Expansion**: Add new player types and goal types.
- **User Interface**: Improve the graphical interface for a more immersive experience.
- **AI Improvements**: Enhance the Smart Player's algorithms for more challenging gameplay.

## Contributing

Feel free to fork the repository and submit pull requests for new features or bug fixes. Contributions are always welcome!

---

Enjoy strategizing your way to victory in Blocky!
