#!/usr/bin/env bash
# Installs the profile README into Heptagon372/Heptagon372 and pushes it.
# Run from inside the unzipped bundle:  bash install.sh
set -euo pipefail

REPO="${1:-https://github.com/Heptagon372/Heptagon372.git}"
SRC="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "→ cloning $REPO"
git clone --quiet "$REPO" "$WORK/repo"
cd "$WORK/repo"

# The current README.md is the upstream profile-site template's docs, not yours.
# Keep it as PROJECT.md so the React app in this repo still has its readme.
if [ -f README.md ] && ! grep -q "assets/header.svg" README.md; then
  echo "→ moving the old README.md to PROJECT.md"
  git mv README.md PROJECT.md
fi

echo "→ copying files in"
cp "$SRC/README.md" "$SRC/SETUP.md" .
mkdir -p assets .fonts .github
cp -R "$SRC/assets/."  assets/
cp -R "$SRC/.fonts/."  .fonts/
cp -R "$SRC/.github/." .github/
find .github -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true

grep -qxF "__pycache__/" .gitignore 2>/dev/null || printf '\n__pycache__/\n' >> .gitignore

if git diff --quiet && git diff --staged --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "nothing to commit — already up to date"
  exit 0
fi

git add -A
git commit --quiet -m "feat: heptagon profile README

Custom purple HUD profile page. Stat cards are generated in-repo by
.github/workflows/cards.yml instead of the public github-readme-stats /
trophy / activity-graph instances, which are down or quota-paused."
echo "→ pushing"
git push

cat <<'EOF'

done. two things left, both in the repo's web UI:

  1. Settings → Actions → General → Workflow permissions
     → "Read and write permissions" → Save

  2. Actions tab → run "Refresh profile cards", then "Generate contribution snake"

The stat cards ship showing "awaiting first Action run" — step 2 replaces
them with your real numbers, and after that they refresh every 6 hours.
EOF
