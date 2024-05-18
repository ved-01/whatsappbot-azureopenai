##### Not used in application, just a different approach for implementing openai
from openai_service import db
from openai import AzureOpenAI
# from langchain.chat_models import AzureChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
load_dotenv()
import os

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment="FAQbot"

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# def generate_response(query, wa_id, name):
    # llm = AzureOpenAI(
    #     deployment_name="FAQbot",
    #     api_key= api_key,
    #     model="gpt-35-turbo",
    #     temperature= 0.7,
    #     api_version="2024-02-01",
        
    # )

    # chain = load_qa_chain(llm, chain_type="stuff")
    # matching_docs = db.similarity_search(query ,k=1)
    # print(matching_docs)
    # print("______________________________")
    # print(len(matching_docs))
    # answer = chain.run(input_documents=matching_docs, question=query)

    # return answer


# query = "Can I claim the 80C deductions at the time of filing the return in case I have not submitted proof to my employer?"
# ans = generate_response(query, "12", "ved")
# print(ans)


      
client = AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)

def getanswer(query, wa_id, name):
    matching_docs = db.similarity_search(query ,k=1)
    page_content = matching_docs[0].page_content
    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the question precisely and to the point only from the given context, if the answer is not present in the context output as Answer for the given query is not present in the context"
            },
            {
                "role": "assistant",
                "content": f"Context: {page_content}",
            },
            {
                "role": "user",
                "content": f"Query: {query}"
            }
        ])
    answer = completion.choices[0].message.content

    return answer

query = "Can I claim the 80C deductions at the time of filing the return in case I have not submitted proof to my employer?"
ans = getanswer(query, "12", "ved")
print(ans)