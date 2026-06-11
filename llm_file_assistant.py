import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import read_file, list_files, write_file, search_in_file

load_dotenv()

MODEL_NAME = "qwen/qwen3-32b"

client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_URL"))


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": """
            List files in a directory.
            Use this tool first to discover resumes.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "extension": {"type": "string"},
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": """
            Read PDF/TXT/DOCX file content.
            """,
            "parameters": {
                "type": "object",
                "properties": {"filepath": {"type": "string"}},
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": """
            Write content to a file.
            Use for creating summaries.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filepath", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": """
            Search keyword inside file.
            Case insensitive.
            Supports pagination and adjustable context window size around matches.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to search in."
                    },
                    "keyword": {
                        "type": "string",
                        "description": "The term or phrase to search for."
                    },
                    "context_size": {
                        "type": "integer",
                        "description": "Number of characters of context to retrieve before and after the keyword match. Defaults to 150."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matches to return (for pagination). Defaults to 10."
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Index of the first match to retrieve (for pagination). Defaults to 0."
                    }
                },
                "required": ["filepath", "keyword"],
            },
        },
    },
]


AVAILABLE_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
    "write_file": write_file,
    "search_in_file": search_in_file,
}


SYSTEM_PROMPT = """
You are a File System Assistant.

Resume files are stored inside:

sample_resumes/

Rules:

1. Never invent file names.
2. Never invent file paths.
3. Always use list_files first.
4. Use read_file to inspect resumes.
5. Use search_in_file for keyword searches.
6. Use write_file for creating summaries.
7. Only answer using tool results.

Examples:

User:
Read all resumes in the resumes folder

You should:
1. List files
2. Read all resumes

User:
Find resumes mentioning Python experience

You should:
1. List files
2. Search each file

User:
Create a summary file for resume_john_doe.pdf

You should:
1. Read resume
2. Create summary
3. Write summary file
"""


def run_assistant(user_query: str):

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL_NAME, messages=messages, tools=TOOLS, tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print("\nAssistant Response:\n")
            print(message.content)
            break

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name

            arguments = json.loads(tool_call.function.arguments)

            print(f"\nCalling Tool: {function_name}")

            print(arguments)

            function_to_call = AVAILABLE_FUNCTIONS[function_name]

            result = function_to_call(**arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result),
                }
            )


if __name__ == "__main__":
    print("LLM File Assistant Started")

    print("Type 'exit' to quit.")

    while True:
        query = input("\nUser > ")

        if query.lower() == "exit":
            break

        run_assistant(query)
