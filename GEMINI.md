# Project Specification: Cartoon-Style Snake Game with Reinforcement Learning

## 1. Project Overview
Develop a Python-based Snake game with a playful, cartoon-style visual identity, paired with a reinforcement learning (RL) pipeline that can train an agent to play it. The system must support both human play and AI play, and the training pipeline must run in two distinct environments: a local machine with a visible game window, and a headless Kaggle notebook with video capture.

## 2. Objectives
- Deliver a polished, entertaining Snake game suitable for manual play.
- Provide a standards-compliant Gymnasium environment that exposes the game as an RL-trainable task.
- Provide a training script that supports both local (rendered) and Kaggle (headless) execution without duplicating game logic.
- Ensure trained models and training footage can be retrieved from Kaggle with minimal manual steps.

## 3. Scope

**In scope:**
- Single-player Snake game with cartoon visual/audio design.
- Human control mode (keyboard) and AI control mode (trained model).
- Custom Gymnasium environment wrapping the core game logic.
- PPO or DQN training via Stable-Baselines3.
- Local live-rendered training and Kaggle headless training with `RecordVideo`.
- Model persistence and a documented Kaggle export/download procedure.

**Out of scope:**
- Multiplayer or networked play.
- Mobile or web deployment.
- Hyperparameter tuning automation (e.g., Optuna sweeps) — sensible defaults are sufficient.

## 4. Functional Requirements

### 4.1 Game Application
| ID | Requirement |
|----|-------------|
| G1 | The game shall be implemented using pygame. |
| G2 | The game shall present a start menu allowing the user to select Human Mode or AI Mode. |
| G3 | In Human Mode, the snake shall be controlled via arrow keys or WASD. |
| G4 | In AI Mode, the snake shall be controlled by a loaded trained model, or by a training agent in real time during live training runs. |
| G5 | The visual style shall be cartoon-like: bright, saturated colors; an animated snake with expressive eyes and a wiggling/squash-stretch movement effect; stylized food sprites (e.g., a wobbling apple, an occasional sparkling bonus item). |
| G6 | The game shall include sound effects for eating and collision/death, and optional background music with a mute toggle. |
| G7 | On collision (self or wall), the game shall play a distinct death animation (e.g., screen shake, an exaggerated "Game Over" banner) before returning to the menu or ending the episode. |
| G8 | The score shall be displayed on-screen and shall increment visibly (e.g., a brief animated "+10" popup) when food is eaten. |
| G9 | During AI Mode, the HUD shall additionally display episode number and cumulative reward. |
| G10 | The game shall support pause, restart, and return-to-menu actions during Human Mode. |
| G11 | The game logic (grid, movement, collision, scoring) shall be implemented independently of the rendering layer, so it can be reused headlessly by the RL environment. |

### 4.2 Reinforcement Learning Environment
| ID | Requirement |
|----|-------------|
| E1 | A `SnakeEnv` class shall be implemented as a subclass of `gymnasium.Env`. |
| E2 | The observation space shall be explicitly defined and documented (e.g., relative food position, movement direction, and danger flags in adjacent cells, or a full grid representation — the chosen design shall be justified in code comments). |
| E3 | The action space shall be `Discrete`, using either absolute directions (4 actions) or relative turns (3 actions); the choice shall be documented. |
| E4 | The reward function shall assign a positive reward for eating food, a negative reward for episode-ending collisions, and, optionally, a small shaping reward for reducing distance to the food. |
| E5 | The environment shall support `render_mode="human"` (live pygame window) and `render_mode="rgb_array"` (for headless video capture). |
| E6 | The environment shall pass validation via `gymnasium.utils.env_checker.check_env`. |

### 4.3 Training Pipeline
| ID | Requirement |
|----|-------------|
| T1 | Training shall be implemented using Stable-Baselines3, defaulting to PPO or DQN (the algorithm shall be selected once and used consistently, with the code structured to allow substitution). |
| T2 | The script shall support two mutually exclusive run modes, selectable via a configuration flag or CLI argument: **Local Mode** and **Kaggle Mode**. |
| T3 | **Local Mode** shall render training live in a pygame window and log episode number, reward, and the algorithm's relevant training metric (e.g., entropy or epsilon) to the console. |
| T4 | **Kaggle Mode** shall run fully headless (e.g., via `SDL_VIDEODRIVER=dummy` and `render_mode="rgb_array"`), with no dependency on a display, and shall be verified compatible with Kaggle's notebook execution environment. |
| T5 | **Kaggle Mode** shall wrap the environment with `gymnasium.wrappers.RecordVideo`, capturing episodes at a configurable interval and saving them as `.mp4` files. |
| T6 | Both modes shall share the same underlying `SnakeEnv` and training logic, differing only in render/display configuration. |
| T7 | Upon completion, the trained model shall be automatically saved to a designated output directory (e.g., `snake_model.zip`); periodic checkpoint saving is recommended but not required. |
| T8 | Training metrics (episode reward, episode length, moving average reward) shall be logged to the console at a minimum, structured so they could be redirected to TensorBoard if desired. |

### 4.4 Kaggle Export Procedure
| ID | Requirement |
|----|-------------|
| K1 | The project shall include a documented procedure (as a notebook cell, script, or README section) for compressing the trained model and recorded videos into a single archive using `zipfile` or `shutil.make_archive`. |
| K2 | The documentation shall explain how to download that archive from Kaggle to a local machine using Kaggle's standard notebook output/download interface. |

## 5. Technical Specifications
- **Language:** Python 3.10+
- **Core libraries:** `pygame`, `gymnasium`, `stable-baselines3`
- **Compatibility:** Local execution (Windows/macOS/Linux with display) and Kaggle notebook execution (headless)
- **Code style:** Modular, with clear separation between game logic, rendering, and RL components; inline comments explaining non-obvious design decisions (observation/action space design, reward shaping, hyperparameters)

## 6. Deliverables
| File | Description |
|------|-------------|
| `snake_game.py` | Standalone playable game supporting Human Mode and AI Mode, with full cartoon UI and audio. |
| `snake_env.py` | Gymnasium-compatible environment wrapping the game logic. |
| `train.py` | Training script supporting Local Mode and Kaggle Mode. |
| `requirements.txt` | Full list of dependencies with versions. |
| `README.md` | Instructions covering: manual play, local training, Kaggle training, loading a saved model to watch the AI play, and the model/video export procedure. |

## 7. Acceptance Criteria
- The game is playable end-to-end in Human Mode with no crashes under normal input.
- `SnakeEnv` passes `check_env` without warnings or errors.
- A short training run (e.g., a few thousand timesteps) completes successfully in both Local Mode and Kaggle Mode.
- A trained model file is produced automatically without manual intervention.
- At least one `.mp4` recording is generated during a Kaggle Mode run.
- The README's Kaggle export steps, when followed, produce a downloadable archive containing both the model and video files.
