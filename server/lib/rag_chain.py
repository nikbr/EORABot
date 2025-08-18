import openai
import re
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

import json

from .config import OPENAI_MODEL, OPENAI_EMBEDDINGS_MODEL, COLLECTION_NAME, VECTOR_STORE_PATH
from .common import ContextEntry

QUESTION_PROMPT = PromptTemplate(
    input_variables=["question", "source_list", "context"],
    template="""Ты ассистент компании EORA. Отвечай на вопросы по-русски.
Используй только предоставленные источники.
После каждого факта добавляй в квадратных скобках номера источников, например [1], [2], [3].
Отвечай в абзаце. Допустимо включать факты из нескольких источников в одно предложение, включайте ссылку после факта([1], [2]...), даже если она находится в середине предложения, и только если факты из разных источников.\n
На пример:\n
\nВопрос: Что вы можете сделать для ритейлеров?
\nОтвет: Например, мы делали бота для HR для Магнита [1], а ещё поиск по картинкам для KazanExpress [2]\n
Не делай такие ответы: Мы решения на базе искусственного интеллекта: разрабатываем чат-ботов, навыки для голосовых ассистентов, боты поддержки, роботов для колл-центров и цифровые аватары, а также специализированные боты для HR и интернет-магазинов [2], [3], [4], [5] 
Если не находишь ответ в источниках, скажи <<У меня нет такой информации.>> и всё.
Не выдумывай источники и не используй посторонние знания.\n
Список источников (используй их номера в ответе) и их фрагменты:\n{context}\n
Вопрос пользователя:\n{question}
"""
)


def get_llm():
    return ChatOpenAI(model=OPENAI_MODEL, temperature="0.3")

def get_embeddings():
    return OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)

def get_vectorstore():
    return Chroma(collection_name=COLLECTION_NAME, embedding_function=get_embeddings(), persist_directory=VECTOR_STORE_PATH)

def get_chain():
    return QUESTION_PROMPT | get_llm() | StrOutputParser()

def create_context(docs: list[Document]) -> tuple[str, dict[int, str]]:
    source_dict = dict()
    n = 1
    for doc in docs:
        url = doc.metadata.get("url")
        title = doc.metadata.get("title")

        if url not in source_dict:
            source_dict[url] = ContextEntry(id=n, title=title, fragments=[doc.page_content])
            n+=1
        else:
            source_dict[url].fragments.append(doc.page_content)

    context_text = ""
    id_dict = dict()
    for key in source_dict:
        val = source_dict[key]
        context_text += "\n" + str(val.id) + " " + val.title
        for fragment in val.fragments:
            context_text += "\n" + fragment
        id_dict[val.id] = key

    return (context_text, id_dict)

def ask_about_eora(question: str) -> dict:
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    docs: list[Document] = retriever.invoke(question)

    context_text, id_dict = create_context(docs)

    chain = get_chain()

    result = chain.invoke({"question":question, "context":context_text})

    try:
        data = dict()
        data["text"] = result
        data["sources"] = id_dict
        return data
    except Exception as e:
        print("Failed to parse LLM output as JSON:", result)
        raise





