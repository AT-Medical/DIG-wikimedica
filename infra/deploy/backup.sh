#!/usr/bin/env bash
# =============================================================================
# backup.sh — Wikimedica Database and Media Backup Script
# =============================================================================
# Dumps the MariaDB database and MediaWiki images volume,
# compresses the archives, uploads to backup storage, and rotates old backups.
#
# Run via cron on the VPS (daily, e.g., 02:00 UTC):
#   0 2 * * * /opt/wikimedica/infra/deploy/backup.sh >> /var/log/wikimedica-backup.log 2>&1
#
# Environment variables (loaded from infra/env/.env):
#   MEDIAWIKI_DB_USER         — MariaDB application user
#   MEDIAWIKI_DB_PASSWORD     — MariaDB application user password
#   MEDIAWIKI_DB_NAME         — Database name
#   MEDIAWIKI_DB_ROOT_PASSWORD — MariaDB root password (for mysqldump)
#   BACKUP_S3_ENDPOINT        — S3-compatible endpoint URL (optional)
#   BACKUP_S3_BUCKET          — S3 bucket name (optional)
#   BACKUP_S3_ACCESS_KEY      — S3 access key (optional)
#   BACKUP_S3_SECRET_KEY      — S3 secret key (optional)
#   BACKUP_SFTP_HOST          — SFTP host (alternative to S3)
#   BACKUP_SFTP_USER          — SFTP username
#   BACKUP_SFTP_PATH          — Remote SFTP path
#   BACKUP_RETAIN_DAYS        — Number of daily backups to retain (default: 7)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEPLOY_DIR="${DEPLOY_DIR:-/opt/wikimedica}"
ENV_FILE="${DEPLOY_DIR}/infra/env/.env"
BACKUP_LOCAL_DIR="${BACKUP_LOCAL_DIR:-${DEPLOY_DIR}/backups}"
BACKUP_RETAIN_DAYS="${BACKUP_RETAIN_DAYS:-7}"

TIMESTAMP=$(date -u '+%Y%m%d_%H%M%S')
BACKUP_PREFIX="wikimedica_${TIMESTAMP}"

DB_CONTAINER="${DB_CONTAINER:-wikimedica_db}"
IMAGES_VOLUME="${IMAGES_VOLUME:-wikimedica_images}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() {
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] BACKUP $*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------

[[ -f "${ENV_FILE}" ]] || fail ".env file not found: ${ENV_FILE}"

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

# ---------------------------------------------------------------------------
# Prepare backup directory
# ---------------------------------------------------------------------------

mkdir -p "${BACKUP_LOCAL_DIR}"
log "Backup directory: ${BACKUP_LOCAL_DIR}"
log "Backup prefix: ${BACKUP_PREFIX}"

# ---------------------------------------------------------------------------
# 1. Database dump
# ---------------------------------------------------------------------------

DB_DUMP_FILE="${BACKUP_LOCAL_DIR}/${BACKUP_PREFIX}_db.sql.gz"

log "Dumping MariaDB database '${MEDIAWIKI_DB_NAME}'..."
docker exec "${DB_CONTAINER}" \
  mysqldump \
    --user=root \
    --password="${MEDIAWIKI_DB_ROOT_PASSWORD}" \
    --single-transaction \
    --routines \
    --triggers \
    --add-drop-table \
    "${MEDIAWIKI_DB_NAME}" \
  | gzip -9 > "${DB_DUMP_FILE}" \
  || fail "Database dump failed"

DB_SIZE=$(du -sh "${DB_DUMP_FILE}" | cut -f1)
log "Database dump complete: ${DB_DUMP_FILE} (${DB_SIZE})"

# ---------------------------------------------------------------------------
# 2. MediaWiki images volume backup
# ---------------------------------------------------------------------------

IMAGES_DUMP_FILE="${BACKUP_LOCAL_DIR}/${BACKUP_PREFIX}_images.tar.gz"

log "Archiving MediaWiki images volume '${IMAGES_VOLUME}'..."
docker run --rm \
  -v "${IMAGES_VOLUME}:/volume:ro" \
  alpine:3 \
  tar czf - -C /volume . \
  > "${IMAGES_DUMP_FILE}" \
  || fail "Images volume backup failed"

IMAGES_SIZE=$(du -sh "${IMAGES_DUMP_FILE}" | cut -f1)
log "Images backup complete: ${IMAGES_DUMP_FILE} (${IMAGES_SIZE})"

# ---------------------------------------------------------------------------
# 3. Upload to backup storage
# ---------------------------------------------------------------------------

upload_to_s3() {
  if [[ -z "${BACKUP_S3_ENDPOINT:-}" ]] || [[ -z "${BACKUP_S3_BUCKET:-}" ]]; then
    log "S3 backup not configured — skipping S3 upload."
    return 0
  fi

  command -v aws &>/dev/null || { log "WARNING: aws CLI not found; skipping S3 upload."; return 0; }

  log "Uploading backups to S3: s3://${BACKUP_S3_BUCKET}/${BACKUP_PREFIX}/"

  AWS_ACCESS_KEY_ID="${BACKUP_S3_ACCESS_KEY}" \
  AWS_SECRET_ACCESS_KEY="${BACKUP_S3_SECRET_KEY}" \
  aws s3 cp "${DB_DUMP_FILE}" \
    "s3://${BACKUP_S3_BUCKET}/daily/${BACKUP_PREFIX}_db.sql.gz" \
    --endpoint-url "${BACKUP_S3_ENDPOINT}" \
    || fail "S3 upload of database dump failed"

  AWS_ACCESS_KEY_ID="${BACKUP_S3_ACCESS_KEY}" \
  AWS_SECRET_ACCESS_KEY="${BACKUP_S3_SECRET_KEY}" \
  aws s3 cp "${IMAGES_DUMP_FILE}" \
    "s3://${BACKUP_S3_BUCKET}/daily/${BACKUP_PREFIX}_images.tar.gz" \
    --endpoint-url "${BACKUP_S3_ENDPOINT}" \
    || fail "S3 upload of images backup failed"

  log "S3 upload complete."
}

upload_to_sftp() {
  if [[ -z "${BACKUP_SFTP_HOST:-}" ]] || [[ -z "${BACKUP_SFTP_USER:-}" ]]; then
    log "SFTP backup not configured — skipping SFTP upload."
    return 0
  fi

  command -v rsync &>/dev/null || { log "WARNING: rsync not found; skipping SFTP upload."; return 0; }

  log "Uploading backups via SFTP/rsync to ${BACKUP_SFTP_HOST}..."

  rsync -az --no-perms \
    "${DB_DUMP_FILE}" "${IMAGES_DUMP_FILE}" \
    "${BACKUP_SFTP_USER}@${BACKUP_SFTP_HOST}:${BACKUP_SFTP_PATH:-/backups/wikimedica}/" \
    || fail "SFTP upload failed"

  log "SFTP upload complete."
}

upload_to_s3
upload_to_sftp

# ---------------------------------------------------------------------------
# 4. Rotate old local backups
# ---------------------------------------------------------------------------

log "Rotating local backups older than ${BACKUP_RETAIN_DAYS} days..."
find "${BACKUP_LOCAL_DIR}" -name "wikimedica_*.sql.gz" -mtime +"${BACKUP_RETAIN_DAYS}" -delete
find "${BACKUP_LOCAL_DIR}" -name "wikimedica_*.tar.gz" -mtime +"${BACKUP_RETAIN_DAYS}" -delete
log "Local backup rotation complete."

# ---------------------------------------------------------------------------
# 5. Summary
# ---------------------------------------------------------------------------

log "=== Backup Complete ==="
log "  Database:  ${DB_DUMP_FILE} (${DB_SIZE})"
log "  Images:    ${IMAGES_DUMP_FILE} (${IMAGES_SIZE})"
log "  Retention: ${BACKUP_RETAIN_DAYS} days"
