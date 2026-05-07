from typing import Any, Callable, Literal, Self
from wolflm.model.base import BaseModel
from google.genai import types
from pydantic import Field


class ToolCall(BaseModel):
    """Represents a request for a ToolCall from an LLM"""
    id: str
    name: str
    args: dict[str, Any]


class ToolResponse(BaseModel):
    """Represents a Tool response to be sent to an LLM"""
    id: str
    name: str
    response: dict[str, Any]


class ToolParameter(BaseModel):
    """Represents a parameter to be interpreted and sent by an LLM when requesting a Tool Call"""
    name: str
    type: Literal['string', 'integer', 'array']
    description: str
    required: bool = True
    enum: list[Any] = None
    items: Literal['string', 'integer'] = None

    def model_post_init(self, context):
        if self.type == 'array' and self.items is None:
            raise ValueError(f'array items type not defined for Tool function {self.name} parameter {self.name}')
        elif self.type == 'array':
            self.items = {'type': self.items}
            
        if self.enum is not None and not isinstance(self.enum, list):
            raise ValueError(f'enum of parameter {self.name} with wrong typing')
    
    def to_dict(self):
        result = {
            self.name: {
                'type': self.type,
                'description': self.description,
            }
        }
        if self.enum:
            result['enum'] = self.enum
        if self.items:
            result['items'] = self.items
        return result

    def to_tuple(self):
        result = {
            'type': self.type,
            'description': self.description,
        }
        if self.enum:
            result['enum'] = self.enum
        if self.items:
            result['items'] = self.items
        return self.name, result


class Tool(BaseModel):
    """
    Main class for tool creation
    must receive a function so it can be used as a callable
    """
    name: str
    description: str
    function: Callable[[...], Any] = None  # type: ignore
    parameters: list[ToolParameter] = Field(default_factory=list)
    strict: bool = False

    def __call__(self, **kwargs):
        return self.function(**kwargs)
    
    def set_function(self, function: Callable[[Any], Any]) -> Self:
        self.function = function
        return self

    def add_parameter(self,
        name: str,
        type: Literal['string', 'integer', 'array'],
        description: str,
        required: bool = True,
        enum: list[Any] = None,
        items: Literal['string', 'integer'] = None,
    ) -> Self:
        """Creates a ToolParameter object for the Tool Function"""
        self.parameters.append(ToolParameter(
            name=name, type=type, description=description,
            required=required, enum=enum, items=items
        ))
        return self
    
    def to_gemini(self):
        return types.Tool(function_declarations=[self.to_dict()])
