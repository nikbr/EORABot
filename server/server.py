from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from lib.rag_chain import ask_about_eora
from lib.config import HOST

mcp = FastMCP(
    name = "EORAInfoBot",
    host=HOST,
    port=8050
)

@mcp.tool()
def ask_question(question:str) -> dict:
    answer = ask_about_eora(question)
    if answer:
        return answer
    else:
        return {"error": "На данный момент не можем ответить на ваш вопрос."}

if __name__ == "__main__":
    mcp.run(transport="sse")