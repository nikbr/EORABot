from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from lib.config import VECTOR_STORE_PATH, OPENAI_EMBEDDINGS_MODEL, COLLECTION_NAME
from lib.common import PageContent


def get_links(urls_file_path: str) -> list[str]:
    with open(urls_file_path, "r") as file:
        urls = [line for line in file]
    return urls


def get_page_content(url:str) -> PageContent:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=10000, wait_until='domcontentloaded')
        page.wait_for_selector("div")

        title = page.title()
        html = page.content()
        browser.close()

    if not title: title = url
    text = get_text_from_html(html)
    return PageContent(url = url, title = title, text = text)

def get_text_from_html(html:str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    classes_to_remove = ["uc-fakeform", "t-form__inputsbox", re.compile("successbox"), re.compile("errorbox"), re.compile("textarea")]

    for cname in classes_to_remove:
        for tag in soup.find_all(class_=cname):
            tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    return text

def get_pages(urls : list[str]) -> list[PageContent]:
    return [get_page_content(url) for url in urls]


def pages_to_docs(pages:list[PageContent]) ->  list[Document]:
    docs = []
    for page in pages:
        metadata = {"url":page.url, "title":page.title}
        doc = Document(page_content=page.text, metadata = metadata)
        docs.append(doc)
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64, separators=["\n", ". ", " ", ""])
    chunks = splitter.split_documents(docs)
    return chunks



def main():
    links = get_links("links.txt")
    pages = get_pages(links)
    docs = pages_to_docs(pages)
    emb = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)
    vector_db = Chroma(collection_name=COLLECTION_NAME,
                     embedding_function=emb,
                     persist_directory=VECTOR_STORE_PATH,
                     )
    vector_db.add_documents(docs)




if __name__=="__main__":
    main()