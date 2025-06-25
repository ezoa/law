import streamlit as st
import os
import torch
import warnings
warnings.filterwarnings("ignore")

import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.query import MetadataQuery
import weaviate.classes.config as wc
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import HierarchicalChunker

# --- 1. UI ---

st.title("Attieke AI: 📖Droit Pour Tous⚖️")
st.markdown("Chargement du **Code de la nationalité ivoirienne**")
# Chargement du Code de la nationalité ivoirienne dans Weaviate + RAG avec Cohere

# --- 2. GPU ---

if torch.cuda.is_available():
    st.success(f"✅ GPU actif : {torch.cuda.get_device_name(0)}")
else:
    st.warning("⚠️ GPU non détecté. L'application continue sans GPU.")

# --- 3. Cohere API key ---

cohere_api_key = "JYDiE7R98t6HIfTWnMo62807LJ1dw6uppBg5b8nY"

# --- 4. Connexion à Weaviate ---

client = weaviate.connect_to_wcs(
    cluster_url="https://jvbgyuplrnwfx3k2dmjidg.c0.us-west3.gcp.weaviate.cloud",
    auth_credentials=AuthApiKey("SVJXQ0hNUnNyYTNMN2FWUV9ockdRRXltM0lGcmNQU0w3L0FhUXE4NDZGdW1qNCtzcVpkZ2lzaUdzcTdnPV92MjAw"),
    headers={"X-Cohere-Api-Key": cohere_api_key}
)

# --- 5. Collection ---

collection_name = "docling"
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)

collection = client.collections.create(
    name=collection_name,
    vectorizer_config=wc.Configure.Vectorizer.text2vec_cohere(model="embed-english-light-v3.0"),
    generative_config=wc.Configure.Generative.cohere(model="command-r-plus"),
    properties=[
        wc.Property(name="text", data_type=wc.DataType.TEXT),
        wc.Property(name="title", data_type=wc.DataType.TEXT, skip_vectorization=True),
    ]
)

# --- 6. Chargement du PDF ---
source_urls = ["code.pdf"]
source_titles = ["Ivorian Nationality Code"]

doc_converter = DocumentConverter()
conv_results_iter = doc_converter.convert_all(source_urls)
docs = [result.document for result in conv_results_iter]

chunker = HierarchicalChunker()
texts, titles = [], []

for doc, title in zip(docs, source_titles):
    chunks = list(chunker.chunk(doc))
    for chunk in chunks:
        texts.append(f"{title} {chunk.text}")
        titles.append(title)

# --- 7. Insertion dans Weaviate ---
data = [{"text": text, "title": title} for text, title in zip(texts, titles)]
response = collection.data.insert_many(data)

if response.has_errors:
    st.error(f"❌ Erreurs lors de l'insertion : {response.errors}")
else:
    st.success("✅ Insertion des données réussie.")

# --- 8. Recherche contextuelle ---
st.header("🔍 Recherche contextuelle")
user_query = st.text_input("Entrez une requête (ex : code de nationalité)", "nationalité par filiation")

if user_query:
    prompt = "Quelles sont les lois du {text} ?"
    try:
        response = collection.generate.near_text(
            query=user_query,
            limit=3,
            grouped_task=prompt,
            return_properties=["text", "title"]
        )
        st.markdown(f"🧠 **Prompt généré :** _{prompt.replace('{text}', user_query)}_")
        st.success(response.generated)
    except Exception as e:
        st.error(f"Erreur : {e}")
