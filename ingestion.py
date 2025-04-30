import os
import pandas as pd
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def upload_to_database(csv_file_path):
    print("Starting data ingestion from CSV...")

    # Load CSV
    df = pd.read_csv(csv_file_path, sep=";")

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Fill NaNs with blanks to avoid issues when joining
    df.fillna("", inplace=True)

    # Select relevant columns (you can adjust as needed)
    relevant_columns = [
        'ID', 'DESCRIPTION', 'Attribut1', 'Additional Feature', 'Application',
        'Characteristic', 'Temp', 'Height', 'Length in mm', 'Rating',
        'Material', 'Size', 'Code', 'Joule-integral-Nom (J)', 'LC Risk',
        'Maximum AC Voltage Rating', 'Maximum DC Voltage Rating',
        'Maximum Power Dissipation', 'Mounting', 'Mounting Feature',
        'Number of Terminals', 'Operating Temperature-Max (Cel)',
        'Operating Temperature-Min (Cel)', 'Physical Dimension',
        'Pre-arcing time-Min (ms)', 'Product Diameter', 'Product Length',
        'Rated Breaking Capacity (A)', 'Rated Current (A)', 'Rated Voltage (V)',
        'Rated Voltage(AC) (V)', 'Rated Voltage(DC) (V)'
    ]

    if not all(col in df.columns for col in relevant_columns):
        missing = [col for col in relevant_columns if col not in df.columns]
        raise ValueError(f"Missing expected columns in CSV: {missing}")

    # Concatenate selected columns into a single text string per row
    documents = []
    for _, row in df[relevant_columns].iterrows():
        combined_text = " | ".join(f"{col}: {row[col]}" for col in relevant_columns)
        documents.append(Document(page_content=combined_text, metadata={"ID": row["ID"]}))

    print(f"Loaded {len(documents)} enriched documents.")

    # Optional: Split long text
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks after splitting.")

    # Generate embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Store in FAISS
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local("faiss_parts_db")
    print("FAISS vector store saved as 'faiss_parts_db'.")

