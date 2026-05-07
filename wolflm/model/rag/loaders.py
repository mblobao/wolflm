from wolflm.utils import FILETYPES, TYPEVALUES, FileType, abstract_decorator
from typing import Any, Generator, Optional
from dataclasses import dataclass, field
from pathlib import Path
from tqdm import tqdm


@dataclass(eq=False, order=False)
class Document:
    content: str | bytes
    type: FileType | str
    id: str | None = field(default=None)
    metadata: dict[str , Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.type, FileType):
            if self.type in FILETYPES:
                self.type = FILETYPES.get(self.type)
            elif self.type in TYPEVALUES:
                self.type = TYPEVALUES.get(self.type)
            else:
                raise ValueError('')

        if not isinstance(self.metadata, dict):
            raise TypeError('')
    
    def __getattr__(self, attr: str) -> Any:
        if attr in self.metadata:
            return self.metadata.get(attr)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")
    
    def __str__(self) -> str:
        return str(self.content)
    
    def add_metadata(self, meta: str, value: Any) -> None:
        self.metadata['value'] = value


class Loader:
    def lazy_load(self) -> Generator[Document, None, None]:
        yield Document(
            content=self.get_file_content(),
            type=str(self.path).split('.')[-1],
            metadata={'source': str(self.path)}
        )
    
    def load(self) -> Document:
        return next(self.lazy_load())
    
    @abstract_decorator
    def get_file_content(self):
        pass


class BinaryLoader(Loader):
    def __init__(self, path: str) -> None:
        self.path = path

    def get_file_content(self) -> bytes:
        with open(self.path, 'rb') as file:
            content = file.read()
        return content
        

class TextLoader(Loader):
    def __init__(self,
        path: str,
        encoding: Optional[str] = None
    ) -> None:
        """Initialize with file path."""
        self.path = path
        self.encoding = 'utf-8' if encoding is None else encoding
    
    def get_file_content(self):
        with open(self.path, 'r', encoding=self.encoding) as file:
            text = file.read()
        return text


class DirectoryLoader:
    def __init__(self,
        path: str,
        glob: list[str] | tuple[str] | str = '**/[!.]*',
        loader_cls: Loader = None,
        show_progress: bool = False
    ) -> None:
        self.path = path        
        self.glob = glob
        self.loader_cls = loader_cls
        self.show_progress = show_progress

    def lazy_load(self) -> Generator[Document, None, None]:
        path = Path(self.path)
        if not path.exists():
            raise FileNotFoundError('')
        if not path.is_dir():
            raise NotADirectoryError('')
        
        paths = list()
        if isinstance(self.glob, (list, tuple)):
            paths.extend(path.glob(pattern) for pattern in self.glob)
        elif isinstance(self.glob, str):
            paths = list(path.glob(self.glob))
        else:
            raise TypeError('')
        
        items = [
            file
            for file in paths
            if (not (self.exclude and any(path.match(glob) for glob in self.exclude)))
            and file.is_file()
        ]

        if self.show_progress:
            items = tqdm(items)
        
        for item in items:
            yield self.loader_cls(item).load()
    
    def load(self) -> list[Document]:
        return list(self.lazy_load())
