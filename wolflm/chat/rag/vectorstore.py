from wolflm.chat.rag.loaders import Document
from typing import Literal, Optional, Self
from wolflm.chat import Chat
from copy import deepcopy
from pathlib import Path
from google import genai
import datetime as dt
from enum import Enum
import chromadb
import os


class GeminiEmbedding(chromadb.EmbeddingFunction):
    class TaskType(Enum):
        SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"  # Used to generate embeddings that are optimized to assess text similarity.
        CLASSIFICATION = "CLASSIFICATION"  # Used to generate embeddings that are optimized to classify texts according to preset labels.
        CLUSTERING = "CLUSTERING"  # Used to generate embeddings that are optimized to cluster texts based on their similarities.
        RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"  # Used to generate embeddings that are optimized for document search or information retrieval.
        RETRIEVAL_QUERY = "RETRIEVAL_QUERY"  # Used to generate embeddings that are optimized for document search or information retrieval.
        QUESTION_ANSWERING = "QUESTION_ANSWERING"  # Used to generate embeddings that are optimized for document search or information retrieval.
        FACT_VERIFICATION = "FACT_VERIFICATION"  # Used to generate embeddings that are optimized for document search or information retrieval.
        CODE_RETRIEVAL_QUERY = "CODE_RETRIEVAL_QUERY"  # Used to retrieve a code block based on a natural language query, such as sort an array or reverse a linked list. Embeddings of the code blocks are computed using RETRIEVAL_DOCUMENT.


    GeminiEmbeddingTypes = Literal["SEMANTIC_SIMILARITY", "CLASSIFICATION", "CLUSTERING", "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY", "QUESTION_ANSWERING", "FACT_VERIFICATION", "CODE_RETRIEVAL_QUERY"]

    def __init__(self,
        task_type: GeminiEmbeddingTypes = None,
        dimension: int = None,
        api_key: str = None
    ) -> None:
        if task_type is None:
            self.task_type = 'RETRIEVAL_DOCUMENT'
        elif task_type in self.TaskType:
            self.task_type = str(task_type).split('.')[-1]
        else:
            raise ValueError('')
        
        self.dimension = 768 if (dimension is None or dimension <= 1) else (1532 if dimension == 2 else 3072)
        
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") if api_key is None else api_key)
    
    def __call__(self, doc: str | Document | list[str | Document]) -> chromadb.Embeddings:
        def set_val(doc: str | Document) -> list[str]:
            if isinstance(doc, str):
                val = [doc]
            elif isinstance(doc, Document):
                val = [doc.content]
            return val
        if isinstance(doc, (str, Document)):
            val = set_val(doc)
        elif isinstance(doc, (list, tuple, set)):
            val = [set_val(d) for d in doc]
        else:
            raise TypeError('')
        
        from google.genai.types import EmbedContentConfig

        embeddings = self.client.models.embed_content(
            model='gemini-embedding-001',
            contents=val,
            config=EmbedContentConfig(task_type=self.task_type, output_dimensionality=self.dimension,)
        )
        return [embed.values for embed in embeddings.embeddings]


class VectorStore:
    class Space:
        L2 = 'l2'
        COSINE = 'cosine'
        IP = 'ip'

    def __init__(self,
        path: str = None,
        embedding_function: chromadb.EmbeddingFunction = None,
        description: str = None,
        space: str = None
    ) -> None:
        if path:
            self.client = chromadb.PersistentClient(Path(path))
        else:
            self.client = chromadb.EphemeralClient()
        
        if not isinstance(embedding_function, chromadb.EmbeddingFunction):
            raise TypeError('')
        self.embedding_function = embedding_function

        self.name = Path(path).name

        self.collection = self.client.get_or_create_collection(
            name=self.name,
            embedding_function=self.embedding_function,
            configuration={
                'hnsw': {  # HNSW = Hierarchical Navigable Small World
                    'space': 'l2' if space is None else str(space),  # 'cosine', 'ip' inner product, 'l2' squared geometric distance
                    # needs to check if the Embedding Function supports the space type  `embeddings.supported_spaces()`

                    'ef_construction': 100,  # determines the size of the candidate list used to select neighbors during index creation.
                    # A higher value improves index quality at the cost of more memory and time, while a lower value speeds up construction with reduced accuracy.
                    # The default value is 100

                    'ef_search': 100,  # determines the size of the dynamic candidate list used while searching for the nearest neighbors.
                    # A higher value improves recall and accuracy by exploring more potential neighbors but increases query time and computational cost,
                    # while a lower value results in faster but less accurate searches. The default value is 100. This field can be modified after creation.

                    'max_neighbors': 16,  # is the maximum number of neighbors (connections) that each node in the graph can have during the construction of the index.
                    # A higher value results in a denser graph, leading to better recall and accuracy during searches but increases memory usage and construction time.
                    # A lower value creates a sparser graph, reducing memory usage and construction time but at the cost of lower search accuracy and recall. The default value is 16.
                
                    'batch_size': 1000,  # determines when to synchronize the index with persistent storage. The default value is 1000. This field can be modified after creation.
                }
            },
            data_loader=None,
            metadata={
                'Description': '' if description is None else description,
                'Created': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    def __len__(self) -> int:
        return self.collection.count()

    def add_to_collection(self, *args: Document) -> Self:
        length = len(self)
        ids, metadatas, documents = list(), list(), list()
        for i, doc in enumerate(args):
            ids.append(str(length + i))
            metadatas.append(doc.metadata)
            documents.append(doc.content)

        self.collection.add(ids=ids, embeddings=None, metadatas=metadatas, documents=documents)
        return self

    def query(self,
        query_texts: list[str],
        n_results: int = 10,
        include: list[Literal["embeddings", "metadatas", "documents", "distances"]] = None,
        ids: list = None,
        where: Optional[chromadb.Where] = None,
        where_document: Optional[chromadb.WhereDocument] = None
    ):
        """
        query_texts=["Orange"], # Chroma will embed this for you
        n_results=1, # how many results to return, default is 10
        include=["embeddings", "metadatas", "documents", "distances"],
        ids=None,  # constrain the search only to records with the IDs from the provided list
 

        where = {
            "metadata_field": {
                '<Operator>': '<Value>'
                # Using the $eq operator is equivalent to using the metadata field directly in your where filter.
            }
        }
        # $eq, $gt, $lt, $gte, $lte
        # $and, $or
        # $in, $nin
        where2 = {
            "metadata_field": '<Value>'
        }

        where3 = {
            "$and": [
                {
                    "metadata_field": {
                        "$nin": ["value1", "value2", "value3"]
                    }
                },
                {
                    "metadata_field": {
                        "$in": ["value1", "value2", "value3"]
                    }
                }
            ]
        }

        collection.get(
        where_document={"$contains": "search string"}
        )

        collection.get(
        where_document={
            "$regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$"
        }
        )

        collection.query(
            query_texts=["query1", "query2"],
            where_document={
                "$and": [
                    {"$contains": "search_string_1"},
                    {"$regex": "[a-z]+"},
                ]
            }
        )

        collection.query(
            query_texts=["query1", "query2"],
            where_document={
                "$or": [
                    {"$contains": "search_string_1"},
                    {"$not_contains": "search_string_2"},
                ]
            }
        )
        """
        return self.collection.query(
            query_embeddings=None, query_images=None, query_uris=None,
            query_texts=query_texts, ids=ids, n_results=n_results, where=where, where_document=where_document,
            include=["metadatas", "documents", "distances"] if include is None else include
        )

    def get(self,
        ids: list = None,
        limit=None,
        offset=None,
        include: list[Literal["embeddings", "metadatas", "documents", "distances"]] = None,
        where: Optional[chromadb.Where] = None,
        where_document: Optional[chromadb.WhereDocument] = None
    ):
        """
        ids=None,  # get records with IDs from this list. If not provided, the first 100 records will be retrieved, in the order of their addition to the collection.
        limit=None,  # the number of records to retrieve. The default value is 100.
        offset=None  # The offset to start returning results from. Useful for paging results with limit. The default value is 0.
        include=["embeddings", "metadatas", "documents"]  # do not supports for distances, the get method only retrieves specified documents

        """
        return self.collection.get(ids=ids, where=where, limit=limit, offset=offset, where_document=where_document,
            include=["metadatas", "documents"] if include is None else include
        )

    def setup_result(self, query_get_result):
        def assemble(doc, meta):
            base = meta['Documento']
            dados = '\n' + '|'.join(f'{k}: {v}' for k, v in meta.items() if k != 'Documento') + '\n'
            return f'<trecho do documento {base}>\n{dados}\n{doc}\n</trecho do documento {base}>'
        result = ["Pode utilizar os trechos abaixo como base de contexto para compor a resposta:"]
        for doc, meta in zip(query_get_result['documents'][0], query_get_result['metadatas'][0]):
            result.append(assemble(doc, meta))
        
        return result

    def setup_prompt(self, chat: Chat, query_get_result):
        result = deepcopy(chat)
        setup_result = self.setup_result(query_get_result)

        if isinstance(chat.messages[-1].content, list):
            result.messages[-1].content.extend(setup_result)
        else:
            result.messages[-1].content = [chat.messages[-1].content] + setup_result
        
        return result


    def delete(self,
        ids: list = None,
        where: Optional[chromadb.Where] = None,
        where_document: Optional[chromadb.WhereDocument] = None
    ) -> None:
        self.collection.delete(ids=ids, where=where, where_document=where_document)
