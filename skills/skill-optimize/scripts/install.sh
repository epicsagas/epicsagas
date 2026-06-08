#!/usr/bin/env bash
# Install SkillOpt engine under this skill directory.
# Usage: bash scripts/install.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILLOPT_DIR="$SKILL_DIR/.skillopt"
REPO_URL="https://github.com/epicsagas/SkillOpt.git"

if [ -d "$SKILLOPT_DIR/.git" ]; then
    echo "✓ SkillOpt already installed at $SKILLOPT_DIR"
    echo "  Updating..."
    (cd "$SKILLOPT_DIR" && git pull --ff-only)
else
    echo "Cloning SkillOpt → $SKILLOPT_DIR"
    git clone "$REPO_URL" "$SKILLOPT_DIR"
fi

if [ ! -f "$SKILLOPT_DIR/.venv/bin/activate" ]; then
    echo "Creating venv..."
    python3 -m venv "$SKILLOPT_DIR/.venv"
    source "$SKILLOPT_DIR/.venv/bin/activate"
    pip install -r "$SKILLOPT_DIR/requirements.txt"
    echo "✓ venv ready"
else
    echo "✓ venv exists"
fi

echo ""
echo "SkillOpt installed. Run: source $SKILLOPT_DIR/.venv/bin/activate"
