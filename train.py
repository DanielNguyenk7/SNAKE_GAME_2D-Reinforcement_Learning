"""
Snake RL training script.

Key upgrades over the original version:
  - Parallel envs (SubprocVecEnv) in kaggle/headless mode for faster, more stable training
  - Monitor wrapping (via make_vec_env) so ep_rew_mean / ep_len_mean are actually visible
  - EvalCallback: tracks and separately saves the BEST model seen during training,
    not just whatever the final checkpoint happens to be
  - CheckpointCallback: periodic saves so a Kaggle timeout/disconnect doesn't lose progress
  - --resume: continue training an existing model across multiple sessions
  - Decoupled video recording: a dedicated single-env callback records one clean,
    complete episode periodically, independent of the parallel training envs
  - --algo ppo|dqn: swap algorithms without touching the rest of the script
  - Slightly stronger default hyperparameters (entropy bonus, larger net, bigger batch)

Requires: pip install moviepy   (needed by gymnasium's RecordVideo for .mp4 encoding)

NOTE: The single biggest factor in final agent quality is usually the reward
shaping and observation design inside snake_env.py, not this script. Worth a
second pass there once this pipeline is running.
"""

import argparse
import os
import zipfile
import torch
import sys

# Ensure the directory containing this script is in the path for subprocesses
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Add Kaggle dataset path if it exists to allow importing snake_env etc.
for path in ["/kaggle/input/datasets/duine2k7/snake-file", "/kaggle/input/duine2k7/snake-file"]:
    if os.path.exists(path):
        sys.path.insert(0, path)

from gymnasium.wrappers import RecordVideo
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback, CheckpointCallback
from stable_baselines3.common.utils import set_random_seed

from snake_env import SnakeEnv

MODEL_DIR = "models"
BEST_MODEL_DIR = os.path.join(MODEL_DIR, "best")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")
EVAL_LOG_DIR = os.path.join(MODEL_DIR, "eval_logs")
VIDEO_DIR = "videos"
TENSORBOARD_DIR = "tb_logs"


def make_snake_env(render_mode=None):
    """Returns a zero-arg factory that builds a raw SnakeEnv instance.
    make_vec_env calls this factory per sub-process and applies Monitor itself."""
    def _create():
        return SnakeEnv(render_mode=render_mode)
    return _create


class VideoRecorderCallback(BaseCallback):
    """Periodically plays one full episode with the current policy in a fresh,
    dedicated headless env and records it. Kept separate from the parallel
    training envs so captures are clean, complete episodes."""

    def __init__(self, video_freq: int, verbose: int = 0):
        super().__init__(verbose)
        self.video_freq = video_freq
        self._last_video_step = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_video_step >= self.video_freq:
            self._last_video_step = self.num_timesteps
            self._record_episode()
        return True

    def _record_episode(self):
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        eval_env = SnakeEnv(render_mode="rgb_array")
        eval_env = RecordVideo(
            eval_env,
            video_folder=VIDEO_DIR,
            episode_trigger=lambda ep: True,
            name_prefix=f"snake_step{self.num_timesteps}",
        )
        obs, _ = eval_env.reset()
        done = False
        while not done:
            action, _ = self.model.predict(obs, deterministic=True)
            obs, _, terminated, truncated, _ = eval_env.step(action)
            done = terminated or truncated
        eval_env.close()
        if self.verbose:
            print(f"[video] recorded snapshot episode at step {self.num_timesteps}")


def build_model(algo: str, env, seed: int, tensorboard_log: str):
    algo = algo.lower()
    if algo == "ppo":
        return PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,          # small exploration bonus, helps avoid early convergence to loops
            policy_kwargs=dict(net_arch=[128, 128]),
            seed=seed,
            tensorboard_log=tensorboard_log,
            device="auto",
        )
    elif algo == "dqn":
        return DQN(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=1e-4,
            buffer_size=100_000,
            learning_starts=5_000,
            batch_size=128,
            gamma=0.99,
            train_freq=4,
            target_update_interval=1_000,
            exploration_fraction=0.2,
            exploration_final_eps=0.02,
            policy_kwargs=dict(net_arch=[128, 128]),
            seed=seed,
            tensorboard_log=tensorboard_log,
        )
    else:
        raise ValueError(f"Unknown algo: {algo}")


def export_kaggle(base_out="/kaggle/working"):
    """Zips the full models/ tree (final + best + checkpoints + eval logs) and videos/."""
    print("Exporting models and videos for Kaggle...")
    zip_path = os.path.join(base_out, "snake_export.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder in (MODEL_DIR, VIDEO_DIR):
            if not os.path.exists(folder):
                print(f"Warning: '{folder}' not found, skipping.")
                continue
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    # We want relative paths inside the zip so they unpack cleanly
                    arcname = os.path.relpath(full_path, base_out)
                    zipf.write(full_path, arcname=arcname)
    print(f"Export complete: '{zip_path}'")


def main():
    parser = argparse.ArgumentParser(description="Train Snake RL Agent")
    parser.add_argument("--mode", choices=["local", "kaggle"], default="local",
                         help="'local' = single env, live pygame render (slow, for watching). "
                              "'kaggle' = headless, parallel envs, periodic video snapshots (fast).")
    parser.add_argument("--algo", choices=["ppo", "dqn"], default="ppo")
    parser.add_argument("--timesteps", type=int, default=1_000_000)
    parser.add_argument("--n-envs", type=int, default=4, help="Parallel envs, kaggle mode only. "
                                                                "Match to available CPU cores.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", type=str, default=None,
                         help="Path to a saved .zip to continue training (must match --algo).")
    parser.add_argument("--checkpoint-freq", type=int, default=50_000, help="Timesteps between checkpoints.")
    parser.add_argument("--eval-freq", type=int, default=25_000, help="Timesteps between evaluations.")
    parser.add_argument("--video-freq", type=int, default=100_000,
                         help="Kaggle mode: timesteps between recorded episode snapshots.")
    args = parser.parse_args()

    # Dynamically resolve directories based on mode to support Kaggle's writable directory
    base_out = "/kaggle/working" if args.mode == "kaggle" else "."
    
    global MODEL_DIR, BEST_MODEL_DIR, CHECKPOINT_DIR, EVAL_LOG_DIR, VIDEO_DIR, TENSORBOARD_DIR
    MODEL_DIR = os.path.join(base_out, "models")
    BEST_MODEL_DIR = os.path.join(MODEL_DIR, "best")
    CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")
    EVAL_LOG_DIR = os.path.join(MODEL_DIR, "eval_logs")
    VIDEO_DIR = os.path.join(base_out, "videos")
    TENSORBOARD_DIR = os.path.join(base_out, "tb_logs")

    set_random_seed(args.seed)
    os.makedirs(BEST_MODEL_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    callbacks = []
    n_envs_used = args.n_envs if args.mode == "kaggle" else 1

    if args.mode == "kaggle":
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        train_env = make_vec_env(
            make_snake_env(render_mode="rgb_array"),
            n_envs=args.n_envs,
            seed=args.seed,
            vec_env_cls=SubprocVecEnv,
        )
        eval_env = make_vec_env(
            make_snake_env(render_mode="rgb_array"),
            n_envs=1,
            seed=args.seed + 999,
            vec_env_cls=DummyVecEnv,
        )
        callbacks.append(VideoRecorderCallback(video_freq=args.video_freq, verbose=1))
    else:
        train_env = make_vec_env(
            make_snake_env(render_mode="human"),
            n_envs=1,
            seed=args.seed,
            vec_env_cls=DummyVecEnv,
        )
        eval_env = make_vec_env(
            make_snake_env(render_mode=None),
            n_envs=1,
            seed=args.seed + 999,
            vec_env_cls=DummyVecEnv,
        )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=BEST_MODEL_DIR,
        log_path=EVAL_LOG_DIR,
        eval_freq=max(args.eval_freq // n_envs_used, 1),
        n_eval_episodes=10,
        deterministic=True,
        render=False,
    )
    checkpoint_callback = CheckpointCallback(
        save_freq=max(args.checkpoint_freq // n_envs_used, 1),
        save_path=CHECKPOINT_DIR,
        name_prefix="snake_ckpt",
    )
    callbacks += [eval_callback, checkpoint_callback]

    if args.resume:
        print(f"Resuming training from {args.resume} (must match --algo {args.algo})")
        model_cls = PPO if args.algo == "ppo" else DQN
        model = model_cls.load(args.resume, env=train_env, tensorboard_log=TENSORBOARD_DIR, device="auto")
    else:
        model = build_model(args.algo, train_env, args.seed, tensorboard_log=TENSORBOARD_DIR)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"--- GPU STATUS ---")
    print(f"PyTorch using device: {device.type.upper()}")
    if device.type == "cuda":
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"------------------")

    print(f"Training {args.algo.upper()} in {args.mode} mode for {args.timesteps} timesteps "
          f"({n_envs_used} env(s))...")
    try:
        model.learn(
            total_timesteps=args.timesteps,
            callback=callbacks,
            reset_num_timesteps=args.resume is None,
        )
    except KeyboardInterrupt:
        print("Training interrupted manually — saving current model before exit.")

    final_path = os.path.join(MODEL_DIR, "snake_model_final")
    model.save(final_path)
    print(f"Final model saved to '{final_path}.zip'")
    print(f"Best-during-training model saved to '{BEST_MODEL_DIR}/best_model.zip'")

    train_env.close()
    eval_env.close()

    if args.mode == "kaggle":
        export_kaggle(base_out)


if __name__ == "__main__":
    main()
