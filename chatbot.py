import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
import google.generativeai as genai

# Set API key directly
api_key = "AIzaSyAKYOsFeGepACfnfbVpXlBLr5JORZP7kCQ"

# Configure Google Generative AI
genai.configure(api_key=api_key)

try:
    # Load CSV data
    df = pd.read_csv("products.csv")

    # Prepare documents
    def row_to_text(row):
         return f"Type: {row['type']}, Size: {row['size']}, URL: {row['url']},Price: {row['price']}"

    texts = [row_to_text(row) for _, row in df.iterrows()]
    docs = [Document(page_content=text) for text in texts]

    # Text splitting
    splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_docs = splitter.split_documents(docs)

    # Create embedding model and vector store
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    db = FAISS.from_documents(split_docs, embedding)

    # Create QA chain with Gemini Pro
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    # Chat loop
    print("🤖 Ask me anything about the clothing products! (Type 'exit' to quit)")
    while True:
        try:
            query = input("\nYou: ").strip()
            if query.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("Please enter a valid question!")
                continue
                
            output = qa({"query": query})
            print("\nBot:", output['result'])
            
        except Exception as e:
            print(f"Error processing your question: {str(e)}")
            print("Please try again with a different question.")

except FileNotFoundError:
    print("Error: products.csv file not found!")
except Exception as e:
    print(f"An error occurred: {str(e)}") 