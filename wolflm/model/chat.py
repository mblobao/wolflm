from wolflm.model.tool import ToolCall, ToolResponse
from typing import Any, Self, overload, Union
from wolflm.model.base import BaseModel, Role
from chromadb.api.types import QueryResult
from wolflm.gemini.utils import get_part
from google.genai import types
from pydantic import Field
from copy import deepcopy
from pathlib import Path


MessageContentPart = Union[Path, str, dict[str, Any], ToolCall, ToolResponse]
MessageContent = Union[MessageContentPart, list[MessageContentPart]]


class Message(BaseModel):
    role: Role | str

    content: MessageContent

    def model_post_init(self, context: Any) -> None:
        self.role  = Role.set_role(self.role)

    def to_gemini(self) -> types.Content:
        role = 'model' if self.role == Role.MODEL else 'user' if self.role in {Role.USER, Role.TOOL} else self.role
        parts = list()
        if isinstance(self.content, (list, tuple)):
            for part in self.content:
                parts.append(get_part(part))
        else:
            parts.append(get_part(self.content))
        
        return types.Content(role=role, parts=parts)

    def to_openai(self):
        raise NotImplementedError()
    
    def to_anthropic(self):
        raise NotImplementedError()
    
    def to_ollama(self):
        raise NotImplementedError()


class Chat(BaseModel):
    messages: list[Message] = Field(default_factory=list)

    iteration: int = -1

    def model_post_init(self, context) -> None:
        self.iteration = -1

    def __iter__(self) -> Self:
        return self
    
    def __next__(self) -> Message:
        try:
            self.iteration += 1
            return self.messages[self.iteration]
        except IndexError:
            self.iteration = -1
            raise StopIteration


    def __getitem__(self, item: int) -> Message:
        return self.messages[item]

    def __len__(self) -> int:
        return len(self.messages)
    
    def clear(self) -> None:
        """Cleans all chat messages."""
        self.messages.clear()

    def copy(self) -> Self:
        return deepcopy(self)

    def get_system_message(self):
        return list(msg for msg in self.messages if msg.role == Role.SYSTEM)
    
    def get_chat(self):
        """Returns only chat user and assistant responses, hiding system, and tool messages"""
        return list(msg for msg in self.messages if msg.role in (Role.MODEL, Role.USER))

    def set_prompt(self, query_result: QueryResult = None) -> Self:
        if not query_result:
            return self
        
        result = deepcopy(self)
        content = result.messages[-1].content

        def assemble(doc, meta):
            base = meta['Documento']
            dados = '\n' + '|'.join(f'{k}: {v}' for k, v in meta.items() if k != 'Documento') + '\n'
            return f'<trecho do documento {base}>\n{dados}\n{doc}\n</trecho do documento {base}>'

        match content:
            case {'role': role, 'parts': parts}:
                result.messages[-1].content
            case str():
                result.messages[-1].content = [
                    content,
                    "Pode utilizar os trechos abaixo como base de contexto para compor a resposta:",
                    *[assemble(doc, meta) for doc, meta in zip(query_result['documents'][0], query_result['metadatas'][0])]
                ]
            case _:
                raise ValueError("Unsupported content format")
        
        return result
    
    def add_message(self, message: Message | MessageContent, role: str = None) -> Self:
        """Adds a message to the conversation history."""
        if isinstance(message, Message):
            self.messages.append(message)
        elif role is None:
            raise ValueError('role must be provided')
        self.messages.append(Message(role=role, content=message))
        return self
    
    def system_message(self, content: str) -> Self:
        return self.add_message(content, role=Role.SYSTEM)
    
    def model_message(self, content: MessageContentPart) -> Self:
        return self.add_message(content, role=Role.MODEL)

    def user_message(self, content: MessageContentPart) -> Self:
        return self.add_message(content, role=Role.USER)
    
    @overload
    def add_tool_call(self, tool_call: ToolCall) -> Self:
        return self.add_message(ToolCall.model_validate(tool_call), role=Role.TOOL)
    
    @overload
    def add_tool_call(self, name: str, args: dict[str, Any], id: str = None) -> Self:
        return self.add_message(ToolCall(id=id, name=name, args=args), role=Role.TOOL)

    @overload
    def add_tool_response(self, tool_response: ToolResponse) -> Self:
        return self.add_message(ToolResponse.model_validate(tool_response), role=Role.TOOL)
    
    @overload
    def add_tool_response(self, name: str, response: dict[str, Any], id: str = None) -> Self:
        return self.add_message(ToolResponse(id=id, name=name, response=response), role=Role.TOOL)

    def to_gemini(self) -> list[dict[str, str | list[dict[str, str]]]]:
        """Returns the message history in Gemini format."""
        return [message.to_gemini() for message in self.messages if message.role != Role.SYSTEM]
    
    def to_openai(self):
        """Returns the message history in OpenAI format."""
        return [message.to_openai() for message in self.messages if message.role != Role.SYSTEM]
    
    def to_anthropic(self):
        """Returns the message history in Anthropic format."""
        return [message.to_anthropic() for message in self.messages if message.role != Role.SYSTEM]
    
    def to_ollama(self):
        """Returns the message history in Ollama format."""
        return [message.to_openai() for message in self.messages if message.role != Role.SYSTEM]
    
