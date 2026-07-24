#!/bin/bash
# EnvironmentNEPAL Article Trimmer
# Keeps max 8 best articles per batch, prioritizing:
# 1. Mongabay Nepal (environment, Nepal-focused) — ALWAYS keep
# 2. Kathmandu Post climate/environment — keep if room
# 3. Ratopati — drop unless clearly environment-related
#
# Usage: cd /path/to/repo && bash scripts/trim_articles.sh

set -e
cd "$(dirname "$0")/.."

echo "[TRIM] Checking for new articles..."

# Find new (today's) articles
TODAY=$(date +%Y-%m-%d)
NEW_FILES=$(find content/news -name "${TODAY}-*.md" -type f | sort)
NEW_COUNT=$(echo "$NEW_FILES" | wc -l | tr -d ' ')
echo "[TRIM] Found ${NEW_COUNT} articles from today"

# Categorize
MONGABAY_FILES=$(echo "$NEW_FILES" | xargs grep -l "Source: Mongabay" 2>/dev/null || echo)
KTM_FILES=$(echo "$NEW_FILES" | xargs grep -l "Source: Kathmandu Post" 2>/dev/null || echo)
RATOPATI_FILES=$(echo "$NEW_FILES" | xargs grep -l "Source: Ratopati" 2>/dev/null || echo)
OTHER_FILES=$(echo "$NEW_FILES" | xargs grep -L "Source: Mongabay\|Source: Kathmandu Post\|Source: Ratopati" 2>/dev/null || echo)

# Build keep list — start with Mongabay (always keep)
KEEP_FILES=""
KEEP_COUNT=0

# Add Mongabay articles
if [ -n "$MONGABAY_FILES" ]; then
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    KEEP_FILES="$KEEP_FILES $file"
    KEEP_COUNT=$((KEEP_COUNT + 1))
    echo "[TRIM] KEEP (Mongabay): $(basename "$file")"
  done <<< "$MONGABAY_FILES"
fi

# Add Kathmandu Post if room
if [ "$KEEP_COUNT" -lt 8 ] && [ -n "$KTM_FILES" ]; then
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    [ "$KEEP_COUNT" -ge 8 ] && break
    # Check if Ktm Post article is actually environment-related
    CATEGORY=$(grep "^Category:" "$file" | head -1 | cut -d' ' -f2)
    if [ "$CATEGORY" = "environment" ] || [ "$CATEGORY" = "climate" ] || [ "$CATEGORY" = "water" ] || [ "$CATEGORY" = "conservation" ]; then
      KEEP_FILES="$KEEP_FILES $file"
      KEEP_COUNT=$((KEEP_COUNT + 1))
      echo "[TRIM] KEEP (KtmPost): $(basename "$file")"
    else
      echo "[TRIM] DROP (KtmPost, non-env): $(basename "$file")"
    fi
  done <<< "$KTM_FILES"
fi

# Check Ratopati for clearly environment-related articles
if [ "$KEEP_COUNT" -lt 8 ] && [ -n "$RATOPATI_FILES" ]; then
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    [ "$KEEP_COUNT" -ge 8 ] && break
    CATEGORY=$(grep "^Category:" "$file" | head -1 | cut -d' ' -f2)
    TITLE=$(grep "^Title:" "$file" | head -1 | sed 's/^Title: //')
    # Only keep Ratopati if clearly environment/climate/water/conservation
    if [ "$CATEGORY" = "environment" ] || [ "$CATEGORY" = "climate" ] || [ "$CATEGORY" = "water" ] || [ "$CATEGORY" = "conservation" ]; then
      KEEP_FILES="$KEEP_FILES $file"
      KEEP_COUNT=$((KEEP_COUNT + 1))
      echo "[TRIM] KEEP (Ratopati-env): $(basename "$file")"
    else
      echo "[TRIM] DROP (Ratopati, non-env): $(basename "$file")"
    fi
  done <<< "$RATOPATI_FILES"
fi

# Add other sources if room
if [ "$KEEP_COUNT" -lt 8 ] && [ -n "$OTHER_FILES" ]; then
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    [ "$KEEP_COUNT" -ge 8 ] && break
    KEEP_FILES="$KEEP_FILES $file"
    KEEP_COUNT=$((KEEP_COUNT + 1))
    echo "[TRIM] KEEP (Other): $(basename "$file")"
  done <<< "$OTHER_FILES"
fi

# Build remove list: all new files NOT in keep list
for file in $NEW_FILES; do
    KEEP=false
    for keep in $KEEP_FILES; do
        if [ "$file" = "$keep" ]; then
            KEEP=true
            break
        fi
    done
    if [ "$KEEP" = false ]; then
        echo "[TRIM] REMOVING: $(basename "$file")"
        rm "$file"
    fi
done

echo "[TRIM] Done. Kept ${KEEP_COUNT} / ${NEW_COUNT} articles."
