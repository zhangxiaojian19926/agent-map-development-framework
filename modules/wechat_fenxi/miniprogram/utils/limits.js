/** Shared product limits. Backend requires this file so the client and server stay in lockstep. */
module.exports = {
  PASTE_INLINE_MAX_BYTES: 64 * 1024,
  FILE_MAX_BYTES: 10 * 1024 * 1024,
  JOBS_JSON_MAX_BYTES: 64 * 1024 + 8 * 1024,
  TTL_MS: 24 * 60 * 60 * 1000,
  CONSENT_VERSION: '2026-10-19',
  ALLOWED_EXT: ['txt', 'json', 'md'],
  POLL_INTERVAL_MS: 1500
}
