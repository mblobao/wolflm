from pathlib import Path
from typing import Self
import pydantic
import json


class Role:
    SYSTEM = 'system'
    MODEL = 'model'
    USER = 'user'
    TOOL = 'tool'

    @classmethod
    def set_role(cls, value: str | Self) -> Self:
        if not isinstance(value, (str, cls)):
            raise ValueError(f'Unrecognized role {value}')
        if isinstance(value, str):
            if value.lower() in ('system', 'developer'):
                return cls.SYSTEM
            elif value.lower() in ('model', 'assistant'):
                return cls.MODEL
            elif value.lower() in ('user', 'human'):
                return cls.USER
            elif value.lower() in ('tool', 'function'):
                return cls.TOOL
        elif isinstance(value, cls):
            return value


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Role):
            return obj.value.lower()
        return super().default(obj)


class BaseModel(pydantic.BaseModel):
    """Base model for all wolflm models"""
    @classmethod
    def model_validate_check(cls, value) -> Self | None:
        try:
            return cls.model_validate(value)
        except pydantic.ValidationError:
            return None
    
    def save(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(mode='python'), f, ensure_ascii=False, indent=4, cls=JsonEncoder)
    
    def json_dumps(self) -> str:
        return json.dumps(self.model_dump(mode='python'), ensure_ascii=False, indent=4, cls=JsonEncoder)

    @classmethod
    def load(cls, path: str | bytes) -> Self:
        if isinstance(path, bytes):
            return cls.model_validate(json.loads(path))
        elif Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return cls.model_validate(json.load(f))
