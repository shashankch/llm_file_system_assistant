# LLM File System Assistant

## Overview

This repository demonstrates an LLM-enabled resume assistant built for recruiter and portfolio use cases. It combines reliable file I/O utilities with function-calling-driven prompt handling to search, inspect, and interact with candidate resumes stored locally.

## Core Capabilities

- Read `.txt`, `.pdf`, and `.docx` resume files and return structured content and metadata
- Recursively list files in a directory with extension filtering and file metadata
- Search resume content for keywords and return contextual matches
- Execute assistant queries through explicit tool functions to minimize hallucination

## Architecture

### `fs_tools.py`

`fs_tools.py` encapsulates file system utilities:

- `read_file(filepath)`
  - Parses `.txt`, `.pdf`, and `.docx`
  - Returns text content and metadata such as filename, absolute path, size, and modification time
- `list_files(directory, extension=None)`
  - Recursively enumerates files under a directory
  - Supports optional extension-based filtering
- `write_file(filepath, content)`
  - Writes UTF-8 text content, creating parent directories as needed
- `search_in_file(filepath, keyword)`
  - Searches file content for a keyword and returns positions plus surrounding context

### `llm_file_assistant.py`

`llm_file_assistant.py` implements the conversational assistant layer:

- Loads environment settings with `python-dotenv`
- Uses the OpenAI client with `LLM_API_KEY` and `LLM_API_URL` for custom endpoints
- Defines tool schemas for `list_files`, `read_file`, `write_file`, and `search_in_file`
- Runs a multi-turn conversation loop with automatic tool execution
- Prints tool calls and arguments for debugging
- Enforces a system prompt with examples that prevents fabrication of filenames and paths

## Setup

1. Create a virtual environment with `uv` ([documentation](https://docs.astral.sh/uv/getting-started/)):

```bash
uv venv .venv
```

2. Install dependencies from `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

3. Add credentials to `.env` in the project root:

```env
LLM_API_KEY=your_api_key_here
LLM_API_URL=your_api_url_here
```

> `llm_file_assistant.py` reads the API key and url from `LLM_API_KEY` and `LLM_API_URL`.

## Usage

Run the assistant from the repository root:

```bash
uv run python llm_file_assistant.py
```

At the prompt, enter recruiter-style commands or natural language queries. Use `exit` to terminate the session.

## Example Queries

- `Search resumes for Python`
- `Find resumes with SQL experience`
- `List all files in sample_resumes`
- `Read sample_resumes/john_doe.txt`

## Project Layout

```text
.
├── fs_tools.py
├── llm_file_assistant.py
├── requirements.txt
├── README.md
└── sample_resumes/
    ├── alex_kumar.docx
    ├── john_doe.pdf
    └── shashank.txt
```

## Notes

- Default resume source directory: `sample_resumes/`
- Supported resume formats: `.txt`, `.pdf`, `.docx`
- The assistant is designed to rely on tool output rather than free-form file generation
- `write_file` tool is available for creating summaries and output files
- Multi-turn conversations are supported—the assistant will make multiple tool calls as needed
