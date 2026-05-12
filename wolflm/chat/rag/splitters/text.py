from wolflm.utils import abstract_decorator
from wolflm.model.rag.loaders import Document
from typing import Literal
from pathlib import Path
import re


class Splitter:
    @abstract_decorator
    def split(self, doc: Document) -> list[Document]:
        pass

    def split_documents(self, docs: list[Document]) -> list[Document]:
        lista = list()
        for doc in docs:
            lista.extend(self.split(doc))
        return lista


class TextSplitter(Splitter):
    def __init__(self,
        chunk_size: int = None,
        chunk_overlap: int | float = None,
        chunk_size_by: Literal['word', 'character'] = None
    ) -> None:
        if chunk_size < 0:
            raise ValueError('')
        if chunk_overlap < 0:
            raise ValueError('')
        if chunk_overlap > chunk_size:
            raise ValueError('')
        
        self.chunk_size = 1000 if chunk_size is None else chunk_size
        self.chunk_overlap = 100 if chunk_overlap is None else chunk_overlap
        self.chunk_size_by = chunk_size_by
    
    def split(self, doc: Document) -> list[Document]:
        if not Document.type.text:
            raise TypeError('')
        
        if self.chunk_size_by == 'character':
            val = doc.content
        elif self.chunk_size_by == 'word':
            val = doc.content.split(' ')
        
        length = len(val)
        a = 0
        b = self.chunk_size
        
        lista: list[Document] = list()
        while b < length:
            lista.append(Document(content=val[a:b], type=doc.type, metadata=doc.metadata))
            a += (self.chunk_size - self.chunk_overlap)
            b = a + self.chunk_size

        return lista


class MarkdownTextSplitter(Splitter):
    def __init__(self,
        header_level_to_split: int = None,
        return_each_line: bool = False,
        strip_headers: bool = True,
    ) -> None:
        if not header_level_to_split:
            self.header_level_to_split = 1
        else:
            self.header_level_to_split = int(header_level_to_split)
        
        self.return_each_line = bool(return_each_line)
        self.strip_headers = bool(strip_headers)

    def split(self, doc: Document) -> list[Document]:
        if doc.type.type not in {'text/md', 'text/plain'}:
            raise TypeError('')
        
        headers = {"#" * i for i in range(1, self.header_level_to_split + 1)}
        
        content = doc.content.split('\n')

        header_lines = [i for i, line in enumerate(content) if any(str(line).startswith(h + ' ') for h in headers)]
        header_lines.append(len(content))

        lista = list()
        for a, b in zip(header_lines[0:-1], header_lines[1:]):
            lista.append(
                Document(
                    content='\n'.join([
                        line
                        for line in content[a:b]
                        if (line != '\n' or self.return_each_line)
                            or (self.strip_headers or not any(str(line).startswith(h + ' ') for h in headers))
                    ]),
                    type=doc.type, metadata=doc.metadata | {'Parte': content[a]}
                )
            )

        return lista


class MarkdownLawSplitter(Splitter):
    PARTS = {
        '#': 'Parte',
        '##': 'Livro',
        '###': 'Título',
        '####': 'Capítulo',
        '#####': 'Secção',
        '######': 'Subseção'
    }

    def split(self, doc: Document | Path) -> list[Document]:
        if isinstance(doc, Document):
            lines = (line for line in doc.content.split('\n'))
            doc_metadata = doc.metadata
        else:
            f = open(doc, 'r', encoding='utf-8')
            lines = (line for line in f.readlines())
            doc_metadata = dict()
        
        split_list = list()
        guides = dict()
        section_content = list()
        
        for line in lines:
            if (match := re.match('(#+) ', line)):
                if section_content:
                    split_list.append(
                        Document(
                            content='\n'.join(section_content),
                            type='text/md',
                            metadata=doc_metadata | {self.PARTS[k]: v for k, v in guides.items()}
                        )
                    )

                guides[match.group(1)] = line.split(' ', maxsplit=1)[-1].split(' - ', maxsplit=1)[-1]
                number = len(match.group(1))

                for k in filter(lambda x: len(x) > number, list(guides.keys())):
                    guides.pop(k)
                
                section_content = list()

            elif (line != '\n' and line != ''):
                section_content.append(line)

        if not isinstance(doc, Document):
            f.close()

        return split_list
