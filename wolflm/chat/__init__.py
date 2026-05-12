from streamlit.runtime.uploaded_file_manager import UploadedFile
from wolflm.chat.tool import ToolCall, ToolResponse
from typing import Any, Generator, Self, Union
from wolflm.chat.base import BaseModel, Role
from chromadb.api.types import QueryResult
from wolflm.utils import FILETYPES
from pydantic import Field
from copy import deepcopy
from pathlib import Path
import base64


PartValue = Union[str, bytes, Path, ToolCall, ToolResponse]

class Part(BaseModel):
    value: PartValue
    mime_type: str | None = None
    bytes_str: bool = False
    rag: bool = False

    def model_post_init(self, context: Any) -> None:
        if isinstance(self.value, bytes) and self.mime_type is None:
            raise TypeError('Cannot set a bytes Part without a defined mime_type')


class Message(BaseModel):
    role: str
    content: Part | list[Part] | Any | list[Any]

    def model_post_init(self, context: Any) -> None:
        self.role  = Role.set_role(self.role)
        if not isinstance(self.content, list):  # Always need to be list
            self.content = [self.content]
        
        content = list()
        for cont in self.content:
            if isinstance(cont, Part):
                content.append(cont)
            elif isinstance(cont, str):
                content.append(Part(value=cont))
            elif isinstance(cont, (list, tuple)):
                params = {k: v for k, v in zip(cont, ('value', 'mime_type', 'bytes_str', 'rag'))}
                content.append(Part(**params))
            else:
                content.append(Part.model_validate(cont))
            
        self.content = content
    
    def no_rag_content(self):
        return Message(role=self.role, content=[part for part in self.content if not part.rag])


class Chat(BaseModel):    
    messages: list[Message] = Field(default_factory=list)

    iteration: int = -1

    def __getitem__(self, item: int) -> Message:
        return self.messages[item]

    def __len__(self) -> int:
        return len(self.messages)
    
    def clear(self) -> None:
        """Cleans all chat messages."""
        self.messages.clear()

    def copy(self) -> Self:
        return deepcopy(self)
    
    def generate_chat(self) -> Generator[Message, None, None]:
        """Returns only chat user and assistant responses, hiding system, and tool messages"""
        return (msg.no_rag_content() for msg in self.messages if msg.role in (Role.MODEL, Role.USER))

    def set_prompt(self, query_result: QueryResult = None, append: bool = False) -> Self:
        if not query_result:
            return self
        
        if append:
            result = self
        else:
            result = deepcopy(self)

        def assemble(doc, meta):
            base = meta['Documento']
            dados = '\n' + '|'.join(f'{k}: {v}' for k, v in meta.items() if k != 'Documento') + '\n'
            return f'<trecho do documento {base}>\n{dados}\n{doc}\n</trecho do documento {base}>'

        result.messages[-1].content.extend(
            [
                "Pode utilizar os trechos abaixo como base de contexto para compor a resposta:",
                *[assemble(doc, meta) for doc, meta in zip(query_result['documents'][0], query_result['metadatas'][0])]
            ]
        )

        return result

    def add_message(self, message: Message | Part, role: str = None) -> Self:
        """Adds a message to the conversation history."""
        if isinstance(message, Message):
            self.messages.append(message)
        elif role is None:
            raise ValueError('role must be provided')
        self.messages.append(Message(role=role, content=message))
        return self
    
    def system_message(self, content: str) -> Self:
        return self.add_message(message=content, role=Role.SYSTEM)
    
    def model_message(self, content: PartValue) -> Self:
        return self.add_message(message=content, role=Role.MODEL)

    def user_message(self, content: PartValue | dict[str, str | list[UploadedFile]]) -> Self:
        if isinstance(content, PartValue):
            return self.add_message(message=content, role=Role.USER)
        
        match content:
            case [*cont] if all(isinstance(c, PartValue) for c in cont):
                return self.add_message(message=content, role=Role.USER)
            case {'text': str(text), 'files': [*files]} if all(isinstance(f, UploadedFile) for f in files):
                parts = [text]

                for file in files:
                    mime_type = FILETYPES[file.type.split('/')[1]].type
                    file_bytes = file.read()
                    parts.append({'bytes': base64.b64encode(file_bytes).decode('utf-8'), 'mime_type': mime_type, 'bytes_str': True})
                
                return self.add_message(message=parts, role=Role.USER)
            case _:
                raise ValueError('Unsupported content format')

    def add_tool_call(self, tool_call_or_name: ToolCall, /, args: dict[str, Any], id: str = None) -> Self:
        if isinstance(tool_call_or_name, str):
            return self.add_message(message=ToolCall(id=id, name=tool_call_or_name, args=args), role=Role.TOOL)
        return self.add_message(message=ToolCall.model_validate(tool_call_or_name), role=Role.TOOL)

    def add_tool_response(self, tool_response_or_name: ToolResponse, /, response: dict[str, Any], id: str = None) -> Self:
        if isinstance(tool_response_or_name, str):
            return self.add_message(message=ToolResponse(id=id, name=tool_response_or_name, response=response), role=Role.TOOL)
        return self.add_message(message=ToolResponse.model_validate(tool_response_or_name), role=Role.TOOL)
