# Snake Game with Reinforcement Learning

A cartoon-style Snake game built in Python, with a Gymnasium environment and a reinforcement learning training pipeline using Stable-Baselines3. The project supports:

- Human gameplay
- AI gameplay using a trained policy
- Local training with live rendering
- Headless training for Kaggle or server environments
- Automatic periodic gameplay video captures

## Features

- Cartoon-inspired visuals and dynamic UI
- Procedural snake, food, and background animations
- Human mode with keyboard controls
- Gymnasium-compatible `SnakeEnv` environment for RL training
- PPO and DQN training support
- Model checkpointing and best-model saving
- Video snapshots during training

## Project Structure

```text
Snake_game/
├── snake_game.py          # game loop and UI
├── snake_env.py           # Gymnasium RL environment
├── train.py               # training script
├── ui_components.py       # reusable UI widgets and theme
├── requirements.txt       # Python dependencies
├── models/                # saved policies, checkpoints, eval logs
├── videos/                # recorded demo videos
├── README.md
├── .gitignore
└── ...
```

## Requirements

This project uses Python 3.10+ and requires the packages in `requirements.txt`.

### Install dependencies

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `moviepy` or `pygame` gives a dependency issue, reinstall the requirements again after activating the venv:

```bash
pip install -r requirements.txt
```

## Run the Game

To launch the menu and play manually:

```bash
python snake_game.py
```

### Controls

- Arrow keys or `W`, `A`, `S`, `D`: move
- `P`: pause / resume
- `R`: restart after game over
- `ESC`: return to menu or quit

## Training the Agent

The main training script is `train.py`.

### 1) Local training (recommended for testing)

This mode uses a single environment and lets you watch training live in the window.

```bash
python train.py --mode local --timesteps 100000
```

This is a good way to check the game runs correctly before a longer training run.

### 2) Full training run

For a larger run, use Kaggle/headless mode or a local machine with more compute:

```bash
python train.py --mode kaggle --timesteps 1000000
```

This mode:

- disables the display driver for headless environments
- uses multiple environments for faster training
- saves checkpoints periodically
- stores the best model in `models/best/`
- writes checkpoints in `models/checkpoints/`
- records short gameplay videos to `videos/`

### 3) Resume training

If you want to continue from an existing model:

```bash
python train.py --mode kaggle --timesteps 1000000 --resume models/best/best_model.zip
```

You can also resume from a checkpoint file inside `models/checkpoints/` if you want to continue from a saved training point.

## Model Output Files

The training script generates these outputs:

- `models/best/` — best-performing saved model
- `models/checkpoints/` — periodic training checkpoints
- `models/eval_logs/` — evaluation metrics
- `videos/` — short recorded gameplay clips
- `tb_logs/` — TensorBoard logs (if enabled)

## Watch the AI Play

Once a trained model is available, launch the game and choose the AI option from the menu.

```bash
python snake_game.py
```

Use the menu option to watch the trained agent play automatically.

## Demo Training Videos

The project includes example training clips at the beginning and near the end of a training run:

- [videos/snake_step100000-episode-0.mp4]<video src="videos/snake_step100000-episode-0.mp4" controls width="600px"></video> — early training demo at step 100000 (begin)
- [videos/snake_step1000000-episode-0.mp4]<video src="videos/snake_step100000-episode-0.mp4" controls width="600px"></video> — final training demo at step 1000000 (final)

These videos help show how the agent develops from a beginner strategy to a stronger, more stable game policy.

## Export for Kaggle or Sharing

In Kaggle/headless mode, the script also creates a zip archive for export:

```bash
snake_export.zip
```

This archive contains the model files and training videos so you can download and reuse them elsewhere.

## Common Troubleshooting

### `pygame` or display errors

If the window does not open correctly, make sure your Python environment is active and requirements are installed.

### Headless environment issues

If you are running on a server or notebook without a display, use:

```bash
python train.py --mode kaggle --timesteps 1000000
```

### Slow training

Start with a smaller run first:

```bash
python train.py --mode local --timesteps 100000
```

Then increase timestep count only after the environment is working correctly.

## Recommended Workflow

1. Create and activate a virtual environment
2. Install `requirements.txt`
3. Run the game once in human mode to confirm it works
4. Run a short training session at 100000 steps
5. Run a longer training session at 1000000 steps
6. Load the trained model and watch AI gameplay

This is the simplest and most reliable path to getting the project running smoothly.
