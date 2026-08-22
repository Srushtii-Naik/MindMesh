#!/usr/bin/env bash
# MindMesh — PostgreSQL backup script.
#
# ROADMAP.md Milestone 12: "Automated PostgreSQL backup strategy implemented
# and tested (restore verified, not just backup)."
#
# In the real deployed environment, Railway's managed PostgreSQL provides
# automated daily snapshots out of the box — this script is the
# supplementary, portable backup path: usable from a CI cron job, a manual
# pre-migration safety snapshot, or (as done for this milestone) local
# verification that backup+restore actually round-trips data correctly.
#
# Usage:
#   DATABASE_URL=postgres://user:pass@host:5432/dbname ./scripts/backup_postgres.sh [output_dir]
#
# Produces output_dir/mindmesh-YYYYmmdd-HHMMSS.sql.gz

set -euo pipefail

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_FILE="${OUTPUT_DIR}/mindmesh-${TIMESTAMP}.sql.gz"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL must be set." >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Backing up database to ${OUTPUT_FILE} ..."
pg_dump --format=plain --no-owner --no-privileges "$DATABASE_URL" | gzip > "$OUTPUT_FILE"

echo "Backup complete: ${OUTPUT_FILE} ($(du -h "$OUTPUT_FILE" | cut -f1))"

# Housekeeping: keep the most recent 14 backups in this directory
# (ARCHITECTURE.md Section 8 — "Housekeeping" background-job category
# covers the equivalent for app data; this mirrors that principle for
# backup retention when this script is run on a schedule).
find "$OUTPUT_DIR" -name 'mindmesh-*.sql.gz' -type f -printf '%T@ %p\n' \
  | sort -rn | tail -n +15 | cut -d' ' -f2- | xargs -r rm -v
