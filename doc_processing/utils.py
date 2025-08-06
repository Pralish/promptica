from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from qdrant_client import QdrantClient,models
from qdrant_client.http.models import PointStruct
import uuid
import re
from django.conf import settings

from openai import OpenAI

client = OpenAI()

def read_data_from_pdf(file):
  text = ""

  with file.open('rb') as file:
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
      text += page.extract_text()
  return text


def get_text_chunks(text):
  text_splitter = CharacterTextSplitter(
    separator="\n",chunk_size=1000,chunk_overlap=200,length_function=len)
  chunks = text_splitter.split_text(text)
  return chunks

def get_embedding(text_chunks, model_id="text-embedding-ada-002"):
    points = []
    for chunk in text_chunks:
        response = client.embeddings.create(
            input=chunk,
            model=model_id
        )
        embedding = response.data[0].embedding  # dot notation
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        ))

    return points

def delete_qdrant_collections():
  client = qdrant_client()

  collections = client.get_collections().collections

  for collection in collections:
      client.delete_collection(collection.name)
      print(f"Deleted collection: {collection.name}")

def create_qdrant_collection(collection_name):
    connection = qdrant_client()
    connection.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    )
    info = connection.get_collection(collection_name=collection_name)

    return info



def make_qdrant_safe(name: str):
    # Replace invalid characters with underscore
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Ensure it doesn't start with a digit
    if safe_name and safe_name[0].isdigit():
        safe_name = 'c_' + safe_name
    return safe_name


name = "Lesson#103_1"
safe_name = make_qdrant_safe(name)
print(safe_name)  # Output: Lesson_103_1


def add_points_qdrant(collection_name, points):
    connection = qdrant_client()
    connection.upsert(collection_name=collection_name, points=points)
    
    return True

def qdrant_client():
  connection = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY)
  return connection