"""SQLx SkillOpt adapter — evaluates MCP tool-call accuracy.

Rollout: sends natural-language requests through claude CLI with the sqlx
skill, captures tool calls from JSON output, and scores against expected
tool + params via exact-match and F1.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from skillopt.datasets.base import BatchSpec, SplitDataLoader
from skillopt.envs.base import EnvAdapter
from skillopt.gradient.reflect import run_minibatch_reflect


class SQLxAdapter(EnvAdapter):
    def __init__(
        self,
        split_dir: str = "",
        split_mode: str = "split_dir",
        workers: int = 4,
        exec_timeout: int = 60,
        analyst_workers: int = 2,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        max_completion_tokens: int = 4096,
        claude_exec_path: str = "claude",
        **kwargs,
    ) -> None:
        self.workers = workers
        self.exec_timeout = exec_timeout
        self.analyst_workers = analyst_workers
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.max_completion_tokens = max_completion_tokens
        self.claude_exec_path = claude_exec_path
        self.dataloader = SplitDataLoader(
            split_dir=os.path.expanduser(split_dir), split_mode=split_mode, **kwargs
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    # ── Batch builders ────────────────────────────────────────────────────

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(
            batch_size=batch_size, seed=seed, **kwargs
        )
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(
            env_num=env_num, split=split, seed=seed, **kwargs
        )
        return self.build_env_from_batch(batch, **kwargs)

    # ── Rollout ───────────────────────────────────────────────────────────

    def rollout(
        self, env_manager, skill_content: str, out_dir: str, **kwargs
    ) -> list[dict]:
        items: list[dict] = env_manager
        os.makedirs(out_dir, exist_ok=True)
        results: list[dict] = []

        def _run_one(item: dict) -> dict:
            return self._evaluate_item(item, skill_content, out_dir)

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(_run_one, item): item for item in items}
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as exc:
                    item = futures[fut]
                    results.append(
                        {
                            "id": str(item.get("id", "")),
                            "task_type": item.get("task_type", "unknown"),
                            "hard": 0,
                            "soft": 0.0,
                            "error": str(exc),
                        }
                    )

        # Persist
        results_path = os.path.join(out_dir, "rollout_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return results

    def _evaluate_item(self, item: dict, skill_content: str, out_dir: str) -> dict:
        """Send request to claude with skill, parse tool call, score."""
        item_id = str(item.get("id", ""))
        user_request = item.get("input", "")
        expected_tool = item.get("expected_tool", "")
        expected_params = item.get("expected_params", {})

        # Build prompt that asks claude to output a single MCP tool call
        prompt = (
            f"Given this skill document:\n\n{skill_content}\n\n"
            f"For the following request, output ONLY a JSON object with "
            f'"tool" and "params" keys. No explanation.\n\n'
            f"Request: {user_request}"
        )

        try:
            result = self._call_claude(prompt)
            parsed = self._parse_tool_call(result)
            hard, soft = self._score(parsed, expected_tool, expected_params)
        except Exception as exc:
            parsed = None
            hard, soft = 0, 0.0

        # Save individual trace
        trace_path = os.path.join(out_dir, f"{item_id}.json")
        with open(trace_path, "w") as f:
            json.dump(
                {
                    "id": item_id,
                    "input": user_request,
                    "expected_tool": expected_tool,
                    "expected_params": expected_params,
                    "predicted": parsed,
                    "hard": hard,
                    "soft": soft,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        return {
            "id": item_id,
            "task_type": item.get("task_type", "unknown"),
            "hard": hard,
            "soft": soft,
        }

    def _call_claude(self, prompt: str) -> str:
        """Call claude CLI with the prompt, return raw text."""
        try:
            proc = subprocess.run(
                [self.claude_exec_path, "--print", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=self.exec_timeout,
            )
            return proc.stdout.strip()
        except subprocess.TimeoutExpired:
            return ""
        except FileNotFoundError:
            raise RuntimeError(f"claude CLI not found at: {self.claude_exec_path}")

    def _parse_tool_call(self, raw: str) -> dict | None:
        """Extract tool + params from claude output."""
        # Try direct JSON parse
        text = raw.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()

        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "tool" in obj:
                return obj
        except json.JSONDecodeError:
            pass

        # Try to find JSON block in text
        import re

        match = re.search(r'\{[^{}]*"tool"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None

    def _score(
        self, predicted: dict | None, expected_tool: str, expected_params: dict
    ) -> tuple[int, float]:
        """Score prediction: hard (exact match), soft (F1 on params)."""
        if predicted is None:
            return 0, 0.0

        pred_tool = predicted.get("tool", "")
        pred_params = predicted.get("params", {})

        if pred_tool != expected_tool:
            return 0, 0.0

        # Tool match — now score params
        if pred_params == expected_params:
            return 1, 1.0

        # Partial credit via F1 on flattened key-value pairs
        expected_flat = self._flatten(expected_params)
        pred_flat = self._flatten(pred_params)

        if not expected_flat:
            return 1, 1.0

        correct = sum(1 for k, v in expected_flat.items() if pred_flat.get(k) == v)
        precision = correct / len(pred_flat) if pred_flat else 0.0
        recall = correct / len(expected_flat) if expected_flat else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return (1 if f1 >= 0.8 else 0), f1

    @staticmethod
    def _flatten(d: dict, parent_key: str = "") -> dict:
        """Flatten nested dict to dot-notation keys."""
        items: dict = {}
        for k, v in d.items():
            key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(SQLxAdapter._flatten(v, key))
            else:
                items[key] = v
        return items

    # ── Reflect prompts ───────────────────────────────────────────────────

    _ERROR_PROMPT = """\
You are a skill document analyst. Given a skill document, a failed task, and the
expected output, produce a JSON patch to improve the skill document.

## Skill Document
{skill}

## Failed Tasks
{results}

## Instructions
1. Identify WHY the skill produced incorrect tool calls for these tasks.
2. Propose minimal edits to the skill document that would fix these failures.
3. Output a JSON object with an "edits" array. Each edit has "path" (section to change)
   and "content" (new content for that section).

Respond with ONLY the JSON patch, no explanation.
"""

    _SUCCESS_PROMPT = """\
You are a skill document analyst. Given a skill document and successful tasks,
identify patterns that work well and suggest reinforcements.

## Skill Document
{skill}

## Successful Tasks
{results}

## Instructions
1. Identify what parts of the skill document are working well for these tasks.
2. Propose minimal edits to reinforce or generalize these successful patterns.
3. Output a JSON object with an "edits" array. Each edit has "path" (section to change)
   and "content" (new content for that section).

Respond with ONLY the JSON patch, no explanation.
"""

    def get_error_minibatch_prompt(self) -> str | None:
        return self._ERROR_PROMPT

    def get_success_minibatch_prompt(self) -> str | None:
        return self._SUCCESS_PROMPT

    # ── Reflect ───────────────────────────────────────────────────────────

    def reflect(
        self, results: list[dict], skill_content: str, out_dir: str, **kwargs
    ) -> list[dict | None]:
        return run_minibatch_reflect(
            results=results,
            skill_content=skill_content,
            prediction_dir=kwargs.get(
                "prediction_dir", os.path.join(out_dir, "predictions")
            ),
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

    # ── Task types ────────────────────────────────────────────────────────

    def get_task_types(self) -> list[str]:
        return ["query", "insert", "update", "delete", "metadata"]
