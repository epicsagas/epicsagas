"""Minimal SkillOpt adapter template.

Copy to: TARGET_DIR/.skillopt/envs/{env_name}/adapter.py
Implement rollout() and evaluator logic per environment.
"""
from __future__ import annotations

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from skillopt.gradient.reflect import run_minibatch_reflect


class TemplateAdapter(EnvAdapter):
    """Template adapter — override rollout() and evaluator per environment."""

    def __init__(
        self,
        split_dir: str = "",
        workers: int = 4,
        exec_timeout: int = 120,
        analyst_workers: int = 2,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        max_completion_tokens: int = 4096,
        **kwargs,
    ) -> None:
        self.workers = workers
        self.exec_timeout = exec_timeout
        self.analyst_workers = analyst_workers
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.max_completion_tokens = max_completion_tokens
        # dataloader setup — use SplitDataLoader subclass
        from skillopt.datasets.base import SplitDataLoader

        self.dataloader = SplitDataLoader(split_dir=split_dir, **kwargs)

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        """Run agent on tasks and evaluate. Implement per environment."""
        raise NotImplementedError("Implement rollout()")

    def reflect(self, results: list[dict], skill_content: str, out_dir: str, **kwargs) -> list[dict | None]:
        import os

        return run_minibatch_reflect(
            results=results,
            skill_content=skill_content,
            prediction_dir=kwargs.get("prediction_dir", os.path.join(out_dir, "predictions")),
            patches_dir=kwargs.get("patches_dir", os.path.join(out_dir, "patches")),
            workers=self.analyst_workers,
            failure_only=getattr(self, "_cfg", {}).get("failure_only", False),
            minibatch_size=self.minibatch_size,
            edit_budget=self.edit_budget,
            random_seed=kwargs.get("random_seed"),
            error_system=self.get_error_minibatch_prompt(),
            success_system=self.get_success_minibatch_prompt(),
            update_mode=getattr(self, "_cfg", {}).get("skill_update_mode", "patch"),
        )

    def get_task_types(self) -> list[str]:
        return ["default"]
