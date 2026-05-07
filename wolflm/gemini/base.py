from wolflm.model.rag.vectorstore import VectorStore
from wolflm.gemini.utils import add_citations
from google.genai import Client, types
from wolflm.model.chat import Chat
from wolflm.models import Model
import os


def generate_content(
    model: str | Model,
    chat: Chat,
    system_instruction=None,
    thinking: bool = False,
    google_search: bool = False,
    vector_space: VectorStore = None,
    api_key: str = None
):
    model_str = model.CodeStr if isinstance(model, Model) else model

    tools, thinking_config = list(), None
    if thinking:
        thinking_config = types.ThinkingConfig(include_thoughts=True)

    if google_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    prompt = chat if vector_space is None else chat.set_prompt(
        vector_space.query(chat.messages[-1].content, n_results=10)
    )

    with Client(api_key=os.getenv("GEMINI_API_KEY") if api_key is None else api_key) as client:
        response = client.models.generate_content(
            model=model_str,
            contents=prompt.to_gemini(),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=None if thinking is None else thinking_config,
                tools=None if tools is None else tools
            )
        )
    
    if google_search:
        response.text = add_citations(response)
    
    return response
