from wolflm.model.tool import ToolCall, ToolResponse
from wolflm.utils import FILETYPES
from google.genai import types
from pathlib import Path
import base64


def get_part(value: str | bytes, mime_type: str = None, bytes_str: bool = False) -> types.Part:
    if isinstance(value, bytes) and mime_type is None:
        raise TypeError('Cannot set a bytes Part without a defined mime_type')
    
    elif isinstance(value, bytes) or bytes_str:
        return types.Part.from_bytes(
            data=base64.b64decode(value.encode('utf-8')) if bytes_str else value,
            mime_type=mime_type
        )

    elif (file_path := Path(value)).is_file():
        mime_type_c = FILETYPES[str(file_path).split('.')[-1].lower()].type if mime_type is None else mime_type
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        return types.Part.from_bytes(data=file_bytes, mime_type=mime_type_c)
    
    elif (val := ToolCall.model_validate_check(value)):
        return types.Part.from_function_call(name=val.name, args=val.args)
    
    elif (val := ToolResponse.model_validate_check(value)):
        return types.Part.from_function_response(name=val.name, response=val.response, parts=val.parts)

    elif isinstance(value, str):
        return types.Part.from_text(text=value)
    
    else:
        match value:
            case [bytes(text), str(m_type)]:
                return types.Part.from_bytes(data=text, mime_type=m_type)
            case {'bytes': bytes(text), 'mime_type': str(m_type)}:
                return types.Part.from_bytes(data=text, mime_type=m_type)
            case _:
                raise TypeError(f'{type(value)}')


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