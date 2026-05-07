from dataclasses import dataclass
from functools import wraps
from pathlib import Path


SKILLS_PATH = Path(__file__).parent / 'skills'
CHATS_PATH = Path(__file__).parent / 'chats'

if str(SKILLS_PATH).startswith('wolflm'):
    SKILLS_PATH = Path('skills')

if str(CHATS_PATH).startswith('wolflm'):
    CHATS_PATH = Path('chats')

def abstract_decorator(method):
    @wraps(method)
    def decorator(self, *args, **kwargs):
        raise NotImplementedError(f'method {method.__name__} must be implemented for class {type(self).__name__}')
    return decorator


@dataclass(frozen=True, eq=False)
class FileType:
    type: str
    text: bool
    image: bool
    binary: bool


FILETYPES = {
    'pdf':        FileType(type='application/pdf', text=False, image=False, binary=True),
    'txt':        FileType(type='text/plain', text=True, image=False, binary=False),
    'json':       FileType(type='application/json', text=True, image=False, binary=False),
    'javascript': FileType(type='application/x-javascript', text=True, image=False, binary=False),
    'js':         FileType(type='application/x-javascript', text=True, image=False, binary=False),
    'python':     FileType(type='application/x-python', text=True, image=False, binary=False),
    'py':         FileType(type='application/x-python', text=True, image=False, binary=False),
    'html':       FileType(type='text/html', text=True, image=False, binary=False),
    'css':        FileType(type='text/css', text=True, image=False, binary=False),
    'markdown':   FileType(type='text/md', text=True, image=False, binary=False),
    'md':         FileType(type='text/md', text=True, image=False, binary=False),
    'csv':        FileType(type='text/csv', text=True, image=False, binary=False),
    'xml':        FileType(type='text/xml', text=True, image=False, binary=False),
    'rtf':        FileType(type='text/rtf', text=True, image=False, binary=False),
    'jpg':        FileType(type='image/jpeg', text=False, image=True, binary=True),
    'jpeg':       FileType(type='image/jpeg', text=False, image=True, binary=True),
    'png':        FileType(type='image/png', text=False, image=True, binary=True),
}

TYPEVALUES = {f.type: f for f in FILETYPES.values()}