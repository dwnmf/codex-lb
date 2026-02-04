# OpenAI Compatibility Rollout Checklist

## Pre-Release

- Run unit tests for OpenAI validation and chat/response mapping.
- Run integration tests for `/v1/responses` and `/v1/chat/completions`.
- Run optional OpenAI client compatibility tests:
  - `RUN_OPENAI_COMPAT=1` + `pytest tests/integration/test_openai_client_compat.py`
- Run optional Codex client compatibility tests:
  - `pytest tests/integration/test_codex_client_compat.py`

## Smoke Tests

- Stream a Responses request and confirm terminal event.
- Stream Chat Completions with `stream_options.include_usage=true`.
- Validate error envelopes for invalid requests.

## Post-Deploy Monitoring

- Watch request logs for spikes in `invalid_request_error`.
- Track `no_accounts` and `stream_incomplete` rates.
- Verify rate-limit headers and usage fields are populated.
