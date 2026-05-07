from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True, eq=False)
class Model:
    DataSet = pd.DataFrame()

    Name: str
    Family: str
    CodeStr: str

    ContextWindow: int

    InputPrice: float = 0.
    OutputPrice: float = 0.

    Description: str = ''

    Batch: bool = False
    Reason: bool = False

    TextInput: bool = False
    TextOutput: bool = False
    PDFInput: bool = False
    ImageInput: bool = False
    ImageOutput: bool = False
    AudioInput: bool = False
    AudioOutput: bool = False
    VideoInput: bool = False
    VideoOutput: bool = False
    
    Embeddings: bool = False

    Function: bool = False
    FileSearch: bool = False
    Maps: bool = False
    Code: bool = False

    def __post_init__(self) -> None:
        cls = type(self)
        cls.DataSet = pd.concat(axis=0,
            objs=[cls.DataSet, pd.DataFrame(self.__dict__, index=[0])]
        ).reset_index(drop=True)

    @classmethod
    def query(cls, qry: str):
        return cls.DataSet.query(qry)


Model(
    Name='Gemini 2.5 Pro', Family='Gemini', CodeStr='gemini-2.5-pro',
    ContextWindow=1048576, Batch=True, Reason=True,
    TextInput=True, PDFInput= True, ImageInput= True, AudioInput= True, VideoInput = True,
    TextOutput= True,
    Function=True, FileSearch = True, Maps = True, Code = True,
)
Model(
    Name='Gemini 2.5 Pro TTS', Family='Gemini', CodeStr='gemini-2.5-pro-preview-tts',
    ContextWindow=8192,
    TextInput=True, AudioOutput= True
)
Model(
    Name='Gemini 2.5 Flash', Family='Gemini', CodeStr='gemini-2.5-flash',
    ContextWindow=1048576, Batch=True, Reason=True,
    TextInput=True, ImageInput= True, AudioInput= True, VideoInput = True,
    TextOutput= True,
    Function=True, FileSearch = True, Maps = True, Code = True,
)
Model(
    Name='Gemini 2.5 Flash TTS', Family='Gemini', CodeStr='gemini-2.5-flash-preview-tts',
    ContextWindow=8192, Batch=True, Reason=True,
    TextInput=True, AudioOutput= True,
)
Model(
    Name='Gemini 2.5 Flash Image', Family='Gemini', CodeStr='gemini-2.5-flash-image',
    ContextWindow=65536, Batch=True,
    TextInput=True, ImageInput= True,
    TextOutput= True, ImageOutput=True
)
Model(
    Name='Imagen 4', Family='Gemini', CodeStr='imagen-4.0-generate-001',
    ContextWindow=480, Batch=True,
    TextInput=True, ImageOutput=True
)
Model(
    Name='Imagen 4 Ultra', Family='Gemini', CodeStr='imagen-4.0-ultra-generate-001',
    ContextWindow=480, Batch=True,
    TextInput=True, ImageOutput=True
)
Model(
    Name='Imagen 4 Fast', Family='Gemini', CodeStr='imagen-4.0-fast-generate-001',
    ContextWindow=480, Batch=True,
    TextInput=True, ImageOutput=True
)
Model(
    Name='Imagen 3', Family='Gemini', CodeStr='imagen-3.0-generate-002',
    ContextWindow=1048576, Batch=True,
    TextInput=True, ImageOutput=True
)
Model(
    Name='Gemini 2.5 Flash-Lite', Family='Gemini', CodeStr='gemini-2.5-flash-lite',
    ContextWindow=1048576, Batch=True, Reason=True,
    TextInput=True, ImageInput= True, AudioInput= True, VideoInput = True,
    TextOutput= True,
    Function=True, FileSearch = True, Maps = True, Code = True,
)
Model(
    Name='Veo 3', Family='Gemini', CodeStr='veo-3.0-generate-001',
    ContextWindow=1024, Batch=True, Reason=True,
    TextInput=True, ImageInput= True, VideoOutput= True,
)
Model(
    Name='Veo 3 Fast', Family='Gemini', CodeStr='veo-3.0-fast-generate-001',
    ContextWindow=1024, Batch=True, Reason=True,
    TextInput=True, ImageInput= True, VideoOutput= True,
)
Model(
    Name='Gemini Embedding 1', Family='Gemini', CodeStr='gemini-embedding-001',
    ContextWindow=2048, Batch=True,
    TextInput=True, Embeddings=True
)