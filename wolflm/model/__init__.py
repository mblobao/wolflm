from streamlit.runtime.uploaded_file_manager import UploadedFile
from wolflm.utils import FILETYPES
from typing import Any


def user_prompt_to_message(text: str, files: list[UploadedFile]) -> list[Any]:
    parts = [text]

    for file in files:
        mime_type = FILETYPES[file.type.split('/')[1]].type
        file_bytes = file.read()
        parts.append({'bytes': file_bytes, 'mime_type': mime_type})
    
    return parts
    
