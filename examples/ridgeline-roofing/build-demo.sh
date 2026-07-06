#!/usr/bin/env bash
# Build the Ridgeline Roofing demo — a fully-populated `administration` site.
#
# Requires `zplus` and `zensical` on PATH (activate the venv that has both).
#   ./build-demo.sh [target-dir]     (default: ~/making/ridgeline-roofing)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SEED="$HERE/seed"
PAGES="$HERE/pages"
TARGET="${1:-$HOME/making/ridgeline-roofing}"

echo "▸ scaffolding $TARGET (administration profile)"
rm -rf "$TARGET"
zplus new "$TARGET" --profile administration >/dev/null
cd "$TARGET"

echo "▸ seeding registries (ref targets)"
for t in role system policy vendor objective constellation; do
  case "$t" in
    constellation) csv="sites" ;;
    policy)        csv="policies" ;;
    *)             csv="${t}s" ;;
  esac
  zplus new-entry --type "$t" --from "$SEED/$csv.csv"
done

echo "▸ seeding templated collections (fields + refs)"
for t in automation agent incident procedure decision; do
  zplus new-entry --type "$t" --from "$SEED/${t}s.csv"
done

echo "▸ populating curated pages"
cp "$PAGES/mission-control.md"       docs/mission-control/index.md
cp "$PAGES/company.md"               docs/company/index.md
cp "$PAGES/mission-vision-values.md" docs/company/mission-vision-values.md
cp "$PAGES/key-facts.md"             docs/company/key-facts.md
cp "$PAGES/how-we-run.md"            docs/how-we-run/index.md
cp "$PAGES/automation-program.md"    docs/automation-program/index.md
cp "$PAGES/division-of-duties.md"    docs/automation-program/division-of-duties.md
mkdir -p docs/reviews
cp "$PAGES/review-june.md"           docs/reviews/2026-06-30-june-monthly-review.md

echo "▸ generating derived views + validating"
zplus gen-derived
zplus check

echo "✔ built $TARGET — run 'cd $TARGET && zplus serve' to view"
