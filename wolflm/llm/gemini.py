from wolflm.chat.rag.vectorstore import VectorStore
from wolflm.chat.tool import ToolCall, ToolResponse
from wolflm.chat import Chat, PartValue, Part
from google.genai import Client, types
from wolflm.llm.models import Model
from wolflm.utils import FILETYPES
from wolflm.chat.base import Role
from google.genai import types
from pathlib import Path
import base64


def generate_content(
    model: str | Model,
    chat: Chat,
    system_instruction=None,
    thinking: bool = False,
    google_search: bool = False,
    vector_space: VectorStore = None,
    api_key: str = None
):
    model_str = model.CodeStr if isinstance(model, Model) else model

    tools, thinking_config = list(), None

    if thinking:
        thinking_config = types.ThinkingConfig(include_thoughts=True)

    if google_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    prompt = chat if vector_space is None else chat.set_prompt(
        vector_space.query(chat.messages[-1].content, n_results=10)
    )

    with Client(api_key=os.getenv("GEMINI_API_KEY") if api_key is None else api_key) as client:
        response = client.models.generate_content(
            model=model_str,
            contents=get_chat(prompt),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=None if thinking is None else thinking_config,
                tools=tools if tools else None
            )
        )
    
    if google_search:
        response.text = add_citations(response)
    
    return response


def get_part(value_or_part: Part | PartValue, /, mime_type: str = None, bytes_str: bool = False) -> types.Part:
    if isinstance(value_or_part, PartValue):
        part = Part(value=value_or_part, mime_type=mime_type, bytes_str=bytes_str)
    else:
        part = value_or_part
    
    if isinstance(part.value, bytes) or bytes_str:
        return types.Part.from_bytes(
            data=base64.b64decode(part.value.encode('utf-8')) if bytes_str else part.value,
            mime_type=mime_type
        )
    elif (file_path := Path(part.value)).is_file():
        mime_type_c = FILETYPES[str(file_path).split('.')[-1].lower()].type if part.mime_type is None else part.mime_type
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        return types.Part.from_bytes(data=file_bytes, mime_type=mime_type_c)
    
    elif (val := ToolCall.model_validate_check(part.value)):
        return types.Part.from_function_call(name=val.name, args=val.args)
    
    elif (val := ToolResponse.model_validate_check(part.value)):
        return types.Part.from_function_response(name=val.name, response=val.response, parts=val.parts)

    elif isinstance(part.value, str):
        return types.Part.from_text(text=part.value)
    

def get_chat(chat: Chat) -> list[types.Content]:
    result = list()
    for message in chat.messages:
        if message.role != Role.SYSTEM:
            parts = list()
            for part in message.content:
                parts.append(get_part(part))
            result.append(types.Content(
                role='model' if message.role == Role.MODEL else 'user' if message.role in {Role.USER, Role.TOOL} else message.role,
                parts=parts
            ))

    return result


def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text
