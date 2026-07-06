# Media Matrix Agent Project Context

Read this file first whenever a new chat or agent starts working on this project.

## Project Goal

Build a Python multi-agent system for operating a self-media content matrix.

Current pipeline:

1. Input one raw topic.
2. `TrendAgent` analyzes trends, pain points, content angles, and keywords.
3. `WriterAgent` generates Xiaohongshu copy and WeChat official account copy.
4. `PublisherAgent` filters sensitive/emotional wording and formats Markdown/HTML publishing output.
5. `main.py` chains the agents into an end-to-end pipeline.
6. `streamlit_app.py` provides a lightweight Web UI.

## Required Working Rules

- After any project change, update this `agent.md` file in the same turn.
- Project changes include code, structure, config, run commands, core behavior, models, agents, or dependencies.
- Create a new git branch before adding any new feature.
- Keep local secrets in `.env` only. `.env` must stay ignored by git.
- Do not copy API keys, tokens, cookies, or other secrets into source code, committed docs, or tracked config files.
- `DeepSeekClient` automatically loads project-root `.env` before reading `DEEPSEEK_*` environment variables.
- Keep the agent structure simple unless the user explicitly asks for a larger framework.
- Prefer Pydantic models for structured LLM output.
- Use `DeepSeekClient.request_structured()` for structured DeepSeek calls.

## Current File Tree

```text
.
|-- agent.md
|-- pyproject.toml
`-- src
    `-- media_matrix
        |-- __init__.py
        |-- client.py
        |-- main.py
        |-- streamlit_app.py
        |-- state.py
        `-- agents
            |-- __init__.py
            |-- base.py
            |-- publisher_agent.py
            |-- trend_agent.py
            `-- writer_agent.py
```

## Core State

File: `src/media_matrix/state.py`

`State` / `AgentState` fields:

- `original_topic`
- `topic` property alias for `original_topic`
- `research_materials`
- `xiaohongshu_copy`
- `wechat_copy`
- `visual_prompt`
- `review_status`
- `trend_result`
- `content_result`
- `current_step`

`TrendAnalysis` fields:

- `pain_points: list[str]`
- `angles: list[str]`
- `keywords: list[str]`

`CopywriteOutput` fields:

- `xiaohongshu_title: str`
- `xiaohongshu_content: str`
- `wechat_title: str`
- `wechat_content: str`

`PublisherOutput` fields:

- `is_safe: bool`
- `risk_reason: Optional[str]`
- `xiaohongshu_markdown: str`
- `wechat_html: str`

`State` also includes:

- `publisher_result: PublisherOutput | None`
- `publish_result` property alias for compatibility

## Implemented Agents

### BaseAgent

File: `src/media_matrix/agents/base.py`

- Base class for all agents.
- Creates `self.llm_client = DeepSeekClient()` in `__init__`.
- Subclasses implement `process(self, state: State) -> State`.

### TrendAgent

File: `src/media_matrix/agents/trend_agent.py`

- Input: `state.topic`
- Output: `state.trend_result`
- Success step: `trend_analyzed`
- Failure step: `trend_failed`
- Structured output model: `TrendAnalysis`

### WriterAgent

File: `src/media_matrix/agents/writer_agent.py`

- Requires `state.trend_result`.
- Skips with `writer_skipped` if no trend result exists.
- Output: `state.content_result`
- Success step: `content_generated`
- Failure step: `writer_failed`
- Structured output model: `CopywriteOutput`

### PublisherAgent

File: `src/media_matrix/agents/publisher_agent.py`

- Requires `state.content_result`.
- Skips with `publisher_skipped` if no content result exists.
- Filters or rewrites sensitive, extreme emotional, absolute-claim, attack, discrimination, medical/financial/job-guarantee style wording.
- Outputs `state.publisher_result` and updates `state.review_status`.
- Success step: `publish_formatted`
- Failure step: `publisher_failed`
- Structured output model: `PublisherOutput`

## DeepSeek Client

File: `src/media_matrix/client.py`

The project currently uses the OpenAI SDK chat completions compatible API.

Environment variables:

```powershell
$env:DEEPSEEK_API_KEY="your-key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
$env:DEEPSEEK_TIMEOUT="120"
$env:DEEPSEEK_MAX_TOKENS="8192"
```

Notes:

- Local testing uses project-root `.env`; do not commit it.
- If `DEEPSEEK_BASE_URL` is set to `https://api.deepseek.com/anthropic`, the client strips `/anthropic` for OpenAI SDK compatibility.
- Correct OpenAI-compatible endpoint for this project: `https://api.deepseek.com/chat/completions` through OpenAI SDK base URL `https://api.deepseek.com`.
- DeepSeek Anthropic-compatible endpoint also works with Anthropic request format at `https://api.deepseek.com/anthropic/v1/messages`, but this project does not use that SDK path.
- Real DeepSeek end-to-end verification has passed with `deepseek-v4-pro`.
- Mock end-to-end verification has also passed.

## Run Command

From the project root:

```powershell
$env:PYTHONPATH="src"
python -m media_matrix.main
```

The DeepSeek settings are loaded from local `.env`.

Pipeline:

```text
TrendAgent -> WriterAgent -> PublisherAgent
```

Frontend:

```powershell
streamlit run src/media_matrix/streamlit_app.py
```

## Current Verification Status

- Python compile check passed.
- Without `DEEPSEEK_API_KEY`, the pipeline fails gracefully at `TrendAgent` with `trend_failed`.
- Mock end-to-end pipeline passed with final step `content_generated`.
- Real DeepSeek E2E passed with `TrendAgent -> WriterAgent`, final step `content_generated`.
- Verified model: `deepseek-v4-pro`.
- Python compile check passed after adding `PublisherAgent` and Streamlit UI.
- Streamlit is available in the current environment (`1.58.0`).
- Streamlit UI uses compatible publisher result lookup to avoid stale-session `State.publisher_result` attribute errors.

## Next Possible Steps

- Add `DesignerAgent` to generate visual prompts from `content_result`.
- Add real publisher-channel export buttons or persistence if needed.
