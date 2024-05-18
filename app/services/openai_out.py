import os
from app.services.openai_service import db
from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
openai_api_version=os.getenv("openai_api_version")


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI


llm = AzureChatOpenAI(
    openai_api_version=openai_api_version,
    azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
)


def getanswer(query):
    docs = db.similarity_search(query)
    message = [
        SystemMessage(
        content=f"""
        You need to answer the query based on below context itself and if the answer is not present, say context doesn't have the answer to required query. Be precise and consise while giving answer.
        
        Context : {docs}"""
        )
        ,
        HumanMessage(
        content=f"""
        
        Query: {query}"""
    )
    ]

    res = llm.invoke(message)
    response = res.content
    return response

# ans = getanswer("Can I claim the 80C deductions at the time of filing the return in case I have not submitted proof to my employer?")
# print(ans)

