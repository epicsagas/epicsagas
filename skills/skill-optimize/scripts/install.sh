#!/usr/bin/env bash
# Install SkillOpt via pip.
# Usage: bash scripts/install.sh
set -euo pipefail

echo "Installing SkillOpt via pip..."
pip install skillopt

# Verify
python -c "import skillopt; print(f'✓ skillopt {skillopt.__version__} installed')" 2>/dev/null || \
    python -c "import skillopt; print('✓ skillopt installed')"

echo ""
echo "SkillOpt ready. Run: python scripts/train.py --config configs/{env_name}/default.yaml"
