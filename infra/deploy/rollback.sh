#!/usr/bin/env bash
# =============================================================================
# rollback.sh — Wikimedica Deployment Rollback Script
# =============================================================================
# Stops the current containers, checks out a previous tag or commit,
# and restarts services.
#
# Usage:
#   ./infra/deploy/rollback.sh <tag-or-commit>
#   ./infra/deploy/rollback.sh v1.1.0
#   ./infra/deploy/rollback.sh abc1234
#
# Environment variables (loaded from infra/env/.env):
#   DEPLOY_DIR    — Absolute path to the repository on the VPS
#   COMPOSE_FILE  — Path to docker-compose.yml
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEPLOY_DIR="${DEPLOY_DIR:-/opt/wikimedica}"
COMPOSE_FILE="${COMPOSE_FILE:-${DEPLOY_DIR}/infra/docker/docker-compose.yml}"
ENV_FILE="${DEPLOY_DIR}/infra/env/.env"
LOG_FILE="${DEPLOY_DIR}/deploy.log"

TARGET="${1:-}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() {
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*" | tee -a "${LOG_FILE}"
}

fail() {
  log "ERROR: $*"
  exit 1
}

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

[[ -n "${TARGET}" ]] || fail "Usage: rollback.sh <tag-or-commit>"
[[ -d "${DEPLOY_DIR}" ]] || fail "Deploy directory not found: ${DEPLOY_DIR}"
[[ -f "${COMPOSE_FILE}" ]] || fail "Docker Compose file not found: ${COMPOSE_FILE}"
[[ -f "${ENV_FILE}" ]] || fail ".env file not found: ${ENV_FILE}"

command -v docker &>/dev/null || fail "docker not found in PATH"
command -v git &>/dev/null || fail "git not found in PATH"

# Load environment
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------

log "=== Wikimedica Rollback Started ==="
log "Rolling back to: ${TARGET}"

cd "${DEPLOY_DIR}"

# Verify the target exists in the repository
git rev-parse "${TARGET}" &>/dev/null || fail "Target '${TARGET}' not found in repository"

# ---------------------------------------------------------------------------
# Stop running services
# ---------------------------------------------------------------------------

log "Stopping running containers..."
docker compose \
  -f "${COMPOSE_FILE}" \
  --env-file "${ENV_FILE}" \
  down \
  || log "WARNING: docker compose down failed — containers may already be stopped"

# ---------------------------------------------------------------------------
# Checkout target
# ---------------------------------------------------------------------------

log "Checking out ${TARGET}..."
git checkout "${TARGET}" || fail "git checkout ${TARGET} failed"

CURRENT_COMMIT=$(git rev-parse --short HEAD)
log "Repository at: ${CURRENT_COMMIT}"

# ---------------------------------------------------------------------------
# Pull images for this version and restart
# ---------------------------------------------------------------------------

log "Pulling Docker images for this version..."
docker compose \
  -f "${COMPOSE_FILE}" \
  --env-file "${ENV_FILE}" \
  pull \
  || log "WARNING: docker compose pull failed — using cached images"

log "Starting services..."
docker compose \
  -f "${COMPOSE_FILE}" \
  --env-file "${ENV_FILE}" \
  up -d \
  || fail "docker compose up failed during rollback"

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

log "Waiting 30 seconds for services to initialise..."
sleep 30

MEDIAWIKI_HEALTH_URL="${MEDIAWIKI_HEALTH_URL:-http://localhost:80/api.php?action=query&format=json}"
if curl -fsS --max-time 10 "${MEDIAWIKI_HEALTH_URL}" &>/dev/null; then
  log "✅ MediaWiki is healthy after rollback."
else
  log "⚠️  WARNING: Health check did not pass. Review container logs:"
  docker compose -f "${COMPOSE_FILE}" logs --tail=50 mediawiki | tee -a "${LOG_FILE}" || true
fi

# ---------------------------------------------------------------------------
# Container status
# ---------------------------------------------------------------------------

log "Container status after rollback:"
docker compose -f "${COMPOSE_FILE}" ps | tee -a "${LOG_FILE}"

log "=== Rollback to ${TARGET} (commit: ${CURRENT_COMMIT}) Complete ==="
log "NOTE: If the rollback required a database schema downgrade, manual database"
log "      restore from backup may be required. See docs/deployment/deployment-model.md"
