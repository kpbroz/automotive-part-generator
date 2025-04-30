import os
from langchain_openai import OpenAIEmbeddings, AzureChatOpenAI, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()


OPENAI_MODEL = os.getenv("OPENAI_MODEL")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_AZURE_ENDPOINT = os.getenv("OPENAI_AZURE_ENDPOINT")

# make chunks of ducumets more readable by adding the newline
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def answer_query(query: str) -> str:
    print(f"Retrieving the answer for you query:  {query}.....")
    
    embeddings = OpenAIEmbeddings()
    llm = ChatOpenAI(temperature=0, stop=["\nObservation"])
    # llm = AzureChatOpenAI(temperature=0, stop=["\nObservation"], model=OPENAI_MODEL, api_key=AZURE_OPENAI_API_KEY, api_version=OPENAI_API_VERSION, azure_endpoint=OPENAI_AZURE_ENDPOINT)
    
    # using pinecone
    # vectorstore =  PineconeVectorStore(
    #     index_name=os.environ["INDEX_NAME"], embedding=embeddings
    # )
    
    # using FAISS
    vectorstore = FAISS.load_local(
        "faiss_parts_db", embeddings, allow_dangerous_deserialization=True
    )
    
    template = """Use the following pieces of context to give response to the user. User may provide part name or part description or both. Generate 5 fictitious parts names and their descriptions based on the context provided for the user query. 
    If the answer doesn't available in the provided context, just say don't know, don't try to make up an answer.
    Always say "thanks!" at the end of the answer.
    
    {context}
    
    Question: {question}
    
    Helpful answer:
    """
    
    custom_rag_prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": vectorstore.as_retriever() | format_docs,   "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
    )
    
    res = rag_chain.invoke(query)
    
    return res.content