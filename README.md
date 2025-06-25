# DroitPourTous with Weaviate and Cohere

This version of the project loads and indexes the *Ivorian Nationality Code* into a Weaviate vector database and enables contextual search with RAG (Retrieval-Augmented Generation) using Cohere.

## Technologies

- **Streamlit** – Web interface
- **Weaviate Cloud** – Vector database (WCS cluster)
- **Cohere** – Text generation API (RAG)
- **Docling** – PDF extraction and hierarchical chunking
- **Google Colab** – Cloud-based runtime with GPU support
- **Ngrok** – Temporary public URL for the app

---

## Project Structure

```
law/
├── main.py                  # Main Streamlit app script
├── code.pdf                 # Legal document to index (Ivorian Nationality Code)
├── requirements.txt         # Required Python packages
├── README.md                # Project description and instructions (this file)
```

---

## How to Run the App (on Google Colab)

1. Upload your `code.pdf` file into `/content/law`
2. Set the following credentials inside `main.py`:
   - `cohere_api_key`: your Cohere API key
   - `AuthApiKey`: your Weaviate API key
   - `cluster_url`: your Weaviate Cloud REST endpoint
3. Run `main.py` to:
   - Extract and chunk the PDF
   - Index data in Weaviate
   - Launch the Streamlit app
4. A public URL will be displayed via Ngrok

---

## Example Queries

You can enter natural language queries such as:

- `"nationalité par filiation"`
- `"perte de nationalité"`
- `"mariage"`

---

## 👨🏾‍💻 Author (Branch: `roland`)
@yves-ro
---

## 📝 License

This project is for research and educational purposes. License terms depend on the original repository policy.