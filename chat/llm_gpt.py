from chat.models import Message
from doc_processing.models import Document
from django.conf import settings
from langchain import OpenAI, ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from qdrant_client import QdrantClient
from doc_processing.utils import make_qdrant_safe 
from openai import OpenAI
import tiktoken

client = OpenAI()

def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def truncate_to_token_limit(text, max_tokens, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return enc.decode(tokens)

def get_final_prompt(query):
    # Create embeddings
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embeddings = response.data[0].embedding

    # Qdrant search
    connection = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    processed_docs = Document.objects.filter(processed_at__isnull=False)
    
    search_results = []
    for document in processed_docs:
        collection_name = f"{document.title}_{document.id}"
        collection_name = make_qdrant_safe(collection_name)
        result = connection.search(
            collection_name=collection_name,
            query_vector=embeddings,
            limit=2  # reduced from 3 to lower total text
        )
        search_results.extend(result)

    # Build prompt from search results
    prompt_parts = [sr.payload["text"] for sr in search_results]
    combined_context = "\n".join(prompt_parts)

    # Truncate context to avoid exceeding token limit
    safe_context = truncate_to_token_limit(combined_context, max_tokens=10000, model="gpt-3.5-turbo")  

    final_prompt = f"""This is the previous data or context:

    {safe_context}

    Here's the user query from the data or context I have provided.
    Do not answer if it is not in the context. Provide the source of the information.

    Question: {query}
    """
    return final_prompt

def get_llm(query, conver_id):
    memory = ConversationBufferMemory()
    if conver_id:
        memorybuffer = Message.objects.filter(
            conversation_id=conver_id).order_by('-created_at')
        for item in memorybuffer:
            memory.chat_memory.add_user_message(item.query)
            memory.chat_memory.add_ai_message(item.response)
        memory.load_memory_variables({})

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
    )
    output = conversation.predict(input=query)
    return output


def get_llm_qdrant(query, conver_id):
    memory = ConversationBufferMemory()
    prompt = get_final_prompt(query)
    memory.chat_memory.add_user_message(prompt)
    memory.load_memory_variables({})


    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
    )

    output = conversation.predict(input=query)

    return output