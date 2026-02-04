# OpenAI Compatibility Notes

This project provides OpenAI-compatible endpoints backed by the ChatGPT upstream.
Compatibility is implemented at the request/response layer with strict validation
and OpenAI-style error envelopes. Behavior is limited by upstream capabilities.

## Supported Endpoints

- `POST /v1/responses`
- `POST /v1/chat/completions`
- `POST /v1/responses/compact` (only if the upstream supports it)

## Request Validation Highlights

- Responses `input` supports string or array; `conversation` and
  `previous_response_id` are mutually exclusive.
- `store=true` is rejected for Responses.
- Chat Completions enforces text-only `system`/`developer` content and supports
  `user` content parts: `text`, `image_url`, `input_audio`, `file`.
- `response_format` is mapped to Responses `text.format` with JSON schema name
  validation (`[A-Za-z0-9_-]{1,64}`).
- Responses `include` values are restricted to:
  - `code_interpreter_call.outputs`
  - `computer_call_output.output.image_url`
  - `file_search_call.results`
  - `message.input_image.image_url`
  - `message.output_text.logprobs`
  - `reasoning.encrypted_content`
  - `web_search_call.action.sources`

## Streaming Behavior

- Responses streams forward upstream event taxonomy and terminate on
  `response.completed`, `response.incomplete`, or `response.failed`.
- Chat Completions are derived from Responses streams, emitting
  `chat.completion.chunk` events and `[DONE]`.
- `stream_options.include_usage` adds a final chunk with `usage` and
  includes `usage: null` on earlier chunks.

## Known Limitations

- Context overflow handling (`truncation=disabled/auto`) is delegated to the
  upstream. This service does not pre-compute token counts.
- Oversized image data URLs (>8MB) are dropped from chat requests.
- Audio input accepts only `wav` and `mp3`.
- Unsupported modalities or provider-specific features are rejected with
  `invalid_request_error`.

## Error Envelope Mapping

Validation errors return:

```
{ "error": { "type": "invalid_request_error", "code": "invalid_request_error", ... } }
```

HTTP errors map to OpenAI-style codes:

- 401 → `invalid_api_key`
- 403 → `insufficient_permissions`
- 404 → `not_found`
- 429 → `rate_limit_exceeded`
- 5xx → `server_error`

Proxy-specific errors include `no_accounts`, `stream_incomplete`,
and `upstream_unavailable`.
