#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Wikimedica Production Deploy Script
# =============================================================================
# Pulls the latest release from GitHub, updates Docker containers,
# performs a health check, and notifies on failure.
#
# Usage (on VPS):
#   ./infra/deploy/deploy.sh [--tag v1.2.3]
#
# Environment variables (set in infra/env/.env or exported before running):
#   DEPLOY_DIR      — Absolute path to the cloned repository on the VPS
#                     Default: /opt/wikimedica
#   COMPOSE_FILE    — Path to docker-compose.yml
#                     Default: ${DEPLOY_DIR}/infra/docker/docker-compose.yml
#   ALERT_EMAIL     — Email to notify on failure (optional)
#   HEALTHCHECK_URL — Healthchecks.io / Uptime Kuma ping URL (optional)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEPLOY_DIR="${DEPLOY_DIR:-/opt/wikimedica}"
COMPOSE_FILE="${COMPOSE_FILE:-${DEPLOY_DIR}/infra/docker/docker-compose.yml}"
ENV_FILE="${DEPLOY_DIR}/infra/env/.env"
LOG_FILE="${DEPLOY_DIR}/deploy.log"
DEPLOY_TAG="${1:-}"  # Optional: --tag v1.2.3

# Health check settings
HEALTH_MAX_RETRIES=12
HEALTH_SLEEP_SECONDS=10
MEDIAWIKI_HEALTH_URL="${MEDIAWIKI_HEALTH_URL:-http://localhost:80/api.php?action=query&format=json}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() {
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*" | tee -a "${LOG_FILE}"
}

fail() {
  log "ERROR: $*"
  notify_failure "$*"
  exit 1
}

notify_failure() {
  local message="$1"
  if [[ -n "${ALERT_EMAIL:-}" ]]; then
    echo "Wikimedica deployment failed: ${message}" \
      | mail -s "[Wikimedica] Deploy FAILED" "${ALERT_EMAIL}" 2>/dev/null || true
  fi
  if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
    curl -fsS --max-time 10 "${HEALTHCHECK_URL}/fail" -d "message=${message}" \
      2>/dev/null || true
  fi
}

notify_success() {
  if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
    curl -fsS --max-time 10 "${HEALTHCHECK_URL}" 2>/dev/null || true
  fi
}

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

log "=== Wikimedica Deploy Started ==="
log "Deploy directory: ${DEPLOY_DIR}"
log "Compose file: ${COMPOSE_FILE}"

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
# Update repository
# ---------------------------------------------------------------------------

log "Changing to deploy directory..."
cd "${DEPLOY_DIR}"

log "Fetching latest changes from origin..."
git fetch origin --tags --prune

if [[ -n "${DEPLOY_TAG}" ]]; then
  log "Checking out tag: ${DEPLOY_TAG}"
  git checkout "${DEPLOY_TAG}" || fail "Failed to checkout tag ${DEPLOY_TAG}"
else
  log "Pulling latest main branch..."
  git checkout main
  git pull origin main --ff-only || fail "git pull failed"
fi

CURRENT_COMMIT=$(git rev-parse --short HEAD)
log "Current commit: ${CURRENT_COMMIT}"

# ---------------------------------------------------------------------------
# Pull updated Docker images
# ---------------------------------------------------------------------------

log "Pulling updated Docker images..."
docker compose \
  -f "${COMPOSE_FILE}" \
  --env-file "${ENV_FILE}" \
  pull \
  || fail "docker compose pull failed"

# ---------------------------------------------------------------------------
# Start/restart services
# ---------------------------------------------------------------------------

log "Starting services with docker compose up..."
docker compose \
  -f "${COMPOSE_FILE}" \
  --env-file "${ENV_FILE}" \
  up -d --remove-orphans \
  || fail "docker compose up failed"

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

log "Waiting for MediaWiki to become healthy..."
RETRIES=0
until curl -fsS --max-time 5 "${MEDIAWIKI_HEALTH_URL}" &>/dev/null; do
  RETRIES=$((RETRIES + 1))
  if [[ ${RETRIES} -ge ${HEALTH_MAX_RETRIES} ]]; then
    # Log container status for debugging
    docker compose -f "${COMPOSE_FILE}" ps >> "${LOG_FILE}" 2>&1 || true
    docker compose -f "${COMPOSE_FILE}" logs --tail=50 mediawiki >> "${LOG_FILE}" 2>&1 || true
    fail "Health check failed after $((HEALTH_MAX_RETRIES * HEALTH_SLEEP_SECONDS)) seconds"
  fi
  log "Health check attempt ${RETRIES}/${HEALTH_MAX_RETRIES} — waiting ${HEALTH_SLEEP_SECONDS}s..."
  sleep "${HEALTH_SLEEP_SECONDS}"
done

log "✅ MediaWiki is healthy."

# ---------------------------------------------------------------------------
# Verify container status
# ---------------------------------------------------------------------------

log "Container status:"
docker compose -f "${COMPOSE_FILE}" ps | tee -a "${LOG_FILE}"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

notify_success
log "=== Wikimedica Deploy Completed Successfully (commit: ${CURRENT_COMMIT}) ==="
