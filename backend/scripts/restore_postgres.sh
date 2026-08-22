#!/usr/bin/env bash
# MindMesh — PostgreSQL restore script.
#
# Companion to backup_postgres.sh. A backup strategy is only real once
# restore has actually been exercised (ROADMAP.md Milestone 12 explicitly
# calls out "restore verified, not just backup") — see README.md's
# Milestone 12 section for the local verification steps run against this
# script.
#
# Usage:
#   DATABASE_URL=postgres://user:pass@host:5432/dbname ./scripts/restore_postgres.sh path/to/backup.sql.gz
#
# WARNING: this drops and recreates the public schema of the TARGET
# database before restoring — do not point this at a database you did not
# intend to overwrite.

set -euo pipefail

BACKUP_FILE="${1:?Usage: restore_postgres.sh path/to/backup.sql.gz}"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL must be set." >&2
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

echo "About to restore ${BACKUP_FILE} into: ${DATABASE_URL}"
echo "This will DROP and recreate the public schema. Press Ctrl+C to abort, or Enter to continue."
read -r _

echo "Dropping and recreating schema..."
psql "$DATABASE_URL" -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'

echo "Restoring from ${BACKUP_FILE} ..."
gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"

echo "Restore complete."
