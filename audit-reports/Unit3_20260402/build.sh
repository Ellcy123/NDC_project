#!/bin/bash
# Assembles the audit report from sections.
# Run from the report directory: bash build.sh
set -e

echo "Assembling NDC Playthrough Audit Report..."

# Verify required files
for f in _base.html _footer.html styles.css main.js; do
  if [ ! -f "$f" ]; then
    echo "ERROR: Missing required file: $f"
    exit 1
  fi
done

# Check sections exist
if [ ! -d sections ] || [ -z "$(ls sections/*.html 2>/dev/null)" ]; then
  echo "ERROR: No section files found in sections/"
  exit 1
fi

# Count sections
section_count=$(ls sections/*.html | wc -l)
echo "Found $section_count sections."

# Assemble
cat _base.html sections/*.html _footer.html > index.html

echo "Built index.html ($section_count sections) — open it in your browser."
echo ""
echo "To view: open index.html in any modern browser."
echo "To export PDF: use the Export PDF button in the report, or Ctrl+P in Chrome."
