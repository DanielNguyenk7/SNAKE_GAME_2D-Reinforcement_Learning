# Cartoon-Style Snake Game with Reinforcement Learning

This project implements a Python-based Snake game with a playful, cartoon-style visual identity, paired with a reinforcement learning (RL) pipeline using `gymnasium` and `stable-baselines3`. The system supports both human play and AI play. The training pipeline can run locally (with live rendering) and headlessly (for platforms like Kaggle).

## Features

* **Cartoon Visuals**: Procedural cartoon graphics including wiggling snake body parts, eyes, and animated food (squash and stretch effects).
* **Audio**: Basic sound generation using Pygame's sndarray for beep sound effects.
* **Human Mode**: Play the game manually using keyboard controls.
* **Gymnasium Environment**: A fully compliant `gymnasium.Env` wrapper (`SnakeEnv`).
* **RL Pipeline**: Train the Snake agent using PPO via Stable-Baselines3.
* **Kaggle Mode**: Fully headless training, recording videos of the agent automatically.

## Requirements

Install the dependencies via:

```bash
pip install -r requirements.txt
```

## How to Play (Human Mode)

You can launch the game and select "Human Mode" from the main menu:

```bash
python snake_game.py
```

* **Controls**: Arrow keys or W, A, S, D to steer.
* **P**: Pause/Unpause.
* **R**: Restart when game over.
* **ESC**: Return to main menu / Quit.

## Training the Agent

The training script `train.py` supports two modes.

### Local Mode (Live Rendering)
To train the agent locally and watch the game as it learns:

```bash
python train.py --mode local --timesteps 100000
```

### Kaggle Mode (Headless + Video Recording)
To train the agent on a headless server like a Kaggle notebook, run:

```bash
python train.py --mode kaggle --timesteps 500000
```

* In Kaggle mode, the script forces `SDL_VIDEODRIVER=dummy` and wraps the environment with `RecordVideo` to capture gameplay every 500 episodes into the `videos/` folder.
* Upon completion, a zipped archive `snake_export.zip` is automatically generated.

## Loading and Watching the AI

Once a model is trained and `snake_model.zip` is saved in the directory, you can watch the AI play by selecting "Watch AI" from the main menu:

```bash
python snake_game.py
```
*(Press `2` on the menu)*

## Kaggle Export Procedure

The `train.py` script automatically zips the trained `snake_model.zip` and the `videos/` folder into a file named `snake_export.zip` when run in `kaggle` mode.

1. Run the training cell in your Kaggle notebook: `!python train.py --mode kaggle`
2. Once complete, refresh your Kaggle output files pane.
3. Download the `snake_export.zip` file directly from the Kaggle interface.
4. Extract locally to review the `.mp4` recordings or run the model using the Human/AI game script.
