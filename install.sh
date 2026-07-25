#!/usr/bin/env bash
# SDD Joedayz Workshop — installer
# Converts package .yaml skills into Claude Code's discovered layout:
#   ~/.claude/skills/<name>/SKILL.md

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}SDD Joedayz Workshop — Installer${NC}"
echo ""
echo -e "${BLUE}Skills destination:${NC} ~/.claude/skills/<name>/SKILL.md"
echo -e "${YELLOW}Note:${NC} flat ~/.claude/skills/common/*.yaml is obsolete and is not loaded."
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Installing PyYAML..."
  python3 -m pip install --user pyyaml
fi

# Preview first
python3 "$ROOT/install_skills.py"
echo ""
read -r -p "Apply install to ~/.claude/skills/? [y/N] " confirm
case "$confirm" in
  y|Y|yes|YES)
    python3 "$ROOT/install_skills.py" --apply
    ;;
  *)
    echo "Cancelled."
    exit 0
    ;;
esac

# Optional templates + memory
TEMPLATES_DIR="$HOME/.claude/sdd-templates"
MEMORY_DIR="$HOME/.sdd/memory"
mkdir -p "$TEMPLATES_DIR" "$MEMORY_DIR"

if [[ -d "$ROOT/templates" ]]; then
  cp -f "$ROOT/templates/CLAUDE.md" "$TEMPLATES_DIR/" 2>/dev/null || true
  cp -f "$ROOT/templates/LEARNINGS.md" "$TEMPLATES_DIR/" 2>/dev/null || true
  cp -f "$ROOT/templates/skill-template.yaml" "$TEMPLATES_DIR/" 2>/dev/null || true
  echo -e "  ${GREEN}✅${NC} templates → $TEMPLATES_DIR"
fi

if [[ -d "$ROOT/memory" ]]; then
  for f in "$ROOT/memory"/*; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    if [[ "$base" == "workshop-learnings.md" && -f "$MEMORY_DIR/$base" ]]; then
      echo -e "  ${YELLOW}⏭${NC} skip existing $base"
      continue
    fi
    cp -f "$f" "$MEMORY_DIR/"
  done
  echo -e "  ${GREEN}✅${NC} memory → $MEMORY_DIR"
fi

echo ""
echo -e "${GREEN}${BOLD}Done.${NC} Ask Claude: \"What SDD skills do I have?\""
echo ""
