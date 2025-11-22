# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Noa Assistant is a multimodal AI assistant API designed for AR smart glasses. It provides conversational AI with vision capabilities, web search, voice transcription, and image generation through a FastAPI server.

## Development Setup

### Environment Configuration
1. Copy `.env.example` to `.env` and configure API keys for:
   - `OPENAI_API_KEY` - Required for Whisper transcription and GPT models
   - `ANTHROPIC_API_KEY` - For Claude models
   - `PERPLEXITY_API_KEY` - For Perplexity web search
   - `SERPAPI_API_KEY` - For SerpAPI web search (optional)
   - `REPLICATE_API_TOKEN` - For image generation (optional)
   - `IMAGE_CDN` - For reverse image search (optional)

2. Install ffmpeg and ensure it's in PATH (required for audio processing)

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

Start the server with default settings:
```bash
python app.py --server
```

With specific providers:
```bash
python app.py --server --vision gpt-4o --search-api perplexity --assistant gpt
```

Available options:
- `--assistant`: `gpt`, `claude`, or `groq` (default: `gpt`)
- `--vision`: `gpt-4o`, `gpt-4-vision-preview`, `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`, `claude-3-opus-20240229`
- `--search-api`: `perplexity`, `serp`, or `dataforseo`

### Testing Queries

Run a single test query:
```bash
python app.py --query "What is this?" --image tests/images/example.jpg --location "San Francisco"
```

Run benchmark tests:
```bash
python run_benchmark.py tests/tests.json
```

Run specific benchmark test:
```bash
python run_benchmark.py tests/tests.json --test "test_name"
```

Generate markdown report from benchmarks:
```bash
python run_benchmark.py tests/tests.json --markdown
```

## Architecture

### Plugin Provider System

The core architecture uses abstract base classes with multiple concrete implementations for each capability:

**Assistant Providers** (`assistant/`):
- `Assistant` (ABC) - Base class defining the assistant interface
- `GPTAssistant` - OpenAI GPT models (also used for Groq)
- `ClaudeAssistant` - Anthropic Claude models

**Vision Providers** (`vision/`):
- `Vision` (ABC) - Base class for vision analysis
- `GPT4Vision` - OpenAI GPT-4 Vision
- `ClaudeVision` - Anthropic Claude Vision

**Web Search Providers** (`web_search/`):
- `WebSearch` (ABC) - Base class for web search
- `PerplexityWebSearch` - Perplexity API
- `SerpWebSearch` - SerpAPI
- `DataForSEOWebSearch` - DataForSEO API

**Image Generation** (`generate_image/`):
- `ReplicateGenerateImage` - Replicate API integration

### Request Flow

1. Client sends POST to `/mm` endpoint with:
   - `mm`: JSON with prompt, messages, location, time, model preferences
   - `audio`: Optional audio file (transcribed via Whisper)
   - `image`: Optional image from camera

2. Server processes request:
   - Transcribes audio if present
   - Selects assistant provider based on request (`get_assistant()`)
   - Selects vision provider (`get_vision_provider()`)
   - Selects web search provider (`get_web_search_provider()`)

3. Assistant executes:
   - Receives prompt, image, message history, location/time context
   - Uses tool calling to invoke web search or vision as needed
   - Returns response with token usage and capabilities used

4. Response includes:
   - Generated text response
   - Optional generated image URL
   - Token usage by model
   - Capabilities used (for quality evaluation)
   - Timing metrics and debug info

### Tool Pattern

Assistants use function calling to invoke tools:
- `web_search` - Current information, products, news, local data
- `general_knowledge_search` - Non-recent trivia (dummy tool, uses assistant knowledge)
- `analyze_photo` - Vision analysis of user's camera feed
- `generate_image` - Image generation from description

The vision tool can trigger a follow-up web search if needed (e.g., for reverse image search or identifying objects).

### Provider Selection

Providers can be specified per-request or use server defaults:
- Request-level: Set in `MultimodalRequest` fields (`assistant`, `vision`, `search_api`)
- User API keys: Clients can provide their own OpenAI/Perplexity keys via request
- Server defaults: Set via command-line args when starting server

### Context Management

The system maintains conversation state through:
- `message_history`: List of prior user/assistant messages
- `learned_context`: Key-value pairs of extracted user facts (not actively used but infrastructure exists)
- `local_time`: User's current time for temporal context
- `location_address`: User's location for search/context

### Audio Processing

Audio files are:
1. Converted to MP4 format using pydub
2. Transcribed using OpenAI Whisper
3. Combined with text prompt if both present
4. In testing mode, saved to `audio/` directory (rotates after 100 files)

## Testing System

The benchmark system (`run_benchmark.py`) evaluates assistant quality:

**Test Format** (`tests/*.json`):
- Each test has a name and conversations
- Conversations are sequences of user messages
- Messages can specify expected capabilities that should be used
- Supports default images for all messages in a test

**Evaluation**:
- Checks if required capabilities were used (web search, vision, etc.)
- Generates markdown reports with timing statistics
- Tracks token usage across conversations

**Running Against Production**:
```bash
python run_benchmark.py tests/tests.json --endpoint https://api.brilliant.xyz/dev/noa/mm --token YOUR_TOKEN
```

## Key Files

- `app.py` - FastAPI server, request handling, provider initialization
- `models/api.py` - Pydantic models for request/response schemas
- `assistant/gpt_assistant.py` - Main GPT-based assistant with tool definitions
- `assistant/claude_assistant.py` - Claude-based assistant implementation
- `vision/utils.py` - Image preprocessing utilities
- `run_benchmark.py` - Testing and evaluation framework
