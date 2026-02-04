from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.types import JsonObject, JsonValue

_RESPONSES_INCLUDE_ALLOWLIST = {
    "code_interpreter_call.outputs",
    "computer_call_output.output.image_url",
    "file_search_call.results",
    "message.input_image.image_url",
    "message.output_text.logprobs",
    "reasoning.encrypted_content",
    "web_search_call.action.sources",
}


class ResponsesReasoning(BaseModel):
    model_config = ConfigDict(extra="allow")

    effort: str | None = None
    summary: str | None = None


class ResponsesTextFormat(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True, serialize_by_alias=True)

    type: str | None = None
    strict: bool | None = None
    schema_: JsonValue | None = Field(default=None, alias="schema")
    name: str | None = None


class ResponsesTextControls(BaseModel):
    model_config = ConfigDict(extra="allow")

    verbosity: str | None = None
    format: ResponsesTextFormat | None = None


class ResponsesRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(min_length=1)
    instructions: str
    input: JsonValue
    tools: list[JsonValue] = Field(default_factory=list)
    tool_choice: str | dict[str, JsonValue] | None = None
    parallel_tool_calls: bool | None = None
    reasoning: ResponsesReasoning | None = None
    store: bool = False
    stream: bool | None = None
    include: list[str] = Field(default_factory=list)
    conversation: str | None = None
    previous_response_id: str | None = None
    truncation: str | None = None
    prompt_cache_key: str | None = None
    text: ResponsesTextControls | None = None

    @field_validator("input")
    @classmethod
    def _validate_input_type(cls, value: JsonValue) -> JsonValue:
        if isinstance(value, str) or isinstance(value, list):
            return value
        raise ValueError("input must be a string or array")

    @field_validator("include")
    @classmethod
    def _validate_include(cls, value: list[str]) -> list[str]:
        for entry in value:
            if entry not in _RESPONSES_INCLUDE_ALLOWLIST:
                raise ValueError(f"Unsupported include value: {entry}")
        return value

    @field_validator("truncation")
    @classmethod
    def _validate_truncation(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in ("auto", "disabled"):
            raise ValueError("truncation must be 'auto' or 'disabled'")
        return value

    @field_validator("store")
    @classmethod
    def _ensure_store_false(cls, value: bool | None) -> bool:
        if value is True:
            raise ValueError("store must be false")
        return False if value is None else value

    @model_validator(mode="after")
    def _validate_conversation(self) -> "ResponsesRequest":
        if self.conversation and self.previous_response_id:
            raise ValueError("Provide either 'conversation' or 'previous_response_id', not both.")
        return self

    def to_payload(self) -> JsonObject:
        payload = self.model_dump(mode="json", exclude_none=True)
        return _strip_unsupported_fields(payload)


class ResponsesCompactRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(min_length=1)
    instructions: str
    input: JsonValue

    @field_validator("input")
    @classmethod
    def _validate_input_type(cls, value: JsonValue) -> JsonValue:
        if isinstance(value, str) or isinstance(value, list):
            return value
        raise ValueError("input must be a string or array")

    def to_payload(self) -> JsonObject:
        payload = self.model_dump(mode="json", exclude_none=True)
        return _strip_unsupported_fields(payload)


_UNSUPPORTED_UPSTREAM_FIELDS = {"max_output_tokens"}


def _strip_unsupported_fields(payload: dict[str, JsonValue]) -> dict[str, JsonValue]:
    for key in _UNSUPPORTED_UPSTREAM_FIELDS:
        payload.pop(key, None)
    return payload
