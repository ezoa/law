import warnings
warnings.filterwarnings("ignore")

import logging
# Suppress Weaviate client logs
logging.getLogger("weaviate").setLevel(logging.ERROR)

import torch
OPENAI_API_KEY=""
# Check if GPU or MPS is available
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"CUDA GPU is enabled: {torch.cuda.get_device_name(0)}")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    print("MPS GPU is enabled.")
else:
    raise EnvironmentError(
        "No GPU or MPS device found. Please check your environment and ensure GPU or MPS support is configured."
)


source_urls = [
    "code.pdf"
   
]
source_titles = [
    "Ivorian Nationality Code ",

]
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

# Instantiate the doc converter
doc_converter = DocumentConverter()

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(source_urls) # previously `convert`

# Iterate over the generator to get a list of Docling documents
docs = [result.document for result in conv_results_iter]

from docling_core.transforms.chunker import HierarchicalChunker

# Initialize lists for text, and titles
texts, titles = [], []

chunker = HierarchicalChunker()

# Process each document in the list
for doc, title in zip(docs, source_titles):       # Pair each document with its title
    chunks = list(chunker.chunk(doc))             # Perform hierarchical chunking and get text from chunks
    for chunk in chunks:
        texts.append(chunk.text)
        titles.append(title)

# Concatenate title and text
for i in range(len(texts)):
    texts[i] = f"{titles[i]} {texts[i]}"

openai_api_key_var = "OPENAI_API_KEY"  # Replace with the name of your secret/env var

# Fetch OpenAI API key
try:
    # If running in Colab, fetch API key from Secrets
    import google.colab
    from google.colab import userdata
    openai_api_key = userdata.get(openai_api_key_var)
    if not openai_api_key:
        raise ValueError(f"Secret '{openai_api_key_var}' not found in Colab secrets.")
except ImportError:
    # If not running in Colab, fetch API key from environment variable
    import os
    openai_api_key = os.getenv(openai_api_key_var)
    if not openai_api_key:
        raise EnvironmentError(
            f"Environment variable '{openai_api_key_var}' is not set. "
            "Please define it before running this script."
        )
import weaviate

# Connect to Weaviate embedded
client = weaviate.connect_to_embedded(
    headers={
        "X-OpenAI-Api-Key": openai_api_key
    }
)

import weaviate.classes.config as wc
from weaviate.classes.config import Property, DataType

# Define the collection name
collection_name = "docling"

# Delete the collection if it already exists
if (client.collections.exists(collection_name)):
    client.collections.delete(collection_name)

# Create the collection
collection = client.collections.create(
    name=collection_name,
    vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-large",                           # Specify your embedding model here
    ),

    # Enable generative model from Cohere
    generative_config=wc.Configure.Generative.openai(
    model="gpt-4o"                                                # Specify your generative model for RAG here
    ),

    # Define properties of metadata
    properties=[
        wc.Property(
            name="text",
            data_type=wc.DataType.TEXT
        ),
        wc.Property(
            name="title",
            data_type=wc.DataType.TEXT,
            skip_vectorization=True
        ),
    ]
)
# Initialize the data object
data = []

# Create a dictionary for each row by iterating through the corresponding lists
for text, title in zip(texts, titles):
    data_point = {
        "text": text,
        "title": title,
    }
    data.append(data_point)

# Insert text chunks and metadata into vector DB collection
response = collection.data.insert_many(
    data
)

if (response.has_errors):
    print(response.errors)
else:
    print("Insert complete.")

from weaviate.classes.query import MetadataQuery

response = collection.query.near_text(
    query="bert",
    limit=2,
    return_metadata=MetadataQuery(distance=True),
    return_properties=["text", "title"]
)

for o in response.objects:
    print(o.properties)
    print(o.metadata.distance)
from rich.console import Console
from rich.panel import Panel

# Create a prompt where context from the Weaviate collection will be injected
prompt = "Quelles sont les loi du {text} "
query = "code de nationalite"

response = collection.generate.near_text(
    query=query,
    limit=3,
    grouped_task=prompt,
    return_properties=["text", "title"]
)

# Prettify the output using Rich
console = Console()

console.print(Panel(f"{prompt}".replace("{text}", query), title="Prompt", border_style="bold red"))
console.print(Panel(response.generated, title="Generated Content", border_style="bold green"))


# # Create a prompt where context from the Weaviate collection will be injected
# prompt = "Explain how {text} works, using only the retrieved context."
# query = "a generative adversarial net"

# response = collection.generate.near_text(
#     query=query,
#     limit=3,
#     grouped_task=prompt,
#     return_properties=["text", "title"]
# )

# # Prettify the output using Rich
# console = Console()

# console.print(Panel(f"{prompt}".replace("{text}", query), title="Prompt", border_style="bold red"))
# console.print(Panel(response.generated, title="Generated Content", border_style="bold green"))
