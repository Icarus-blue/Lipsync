import os
import csv
import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import QAPair
from django.conf import settings
from .form import DocumentUploadForm
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.llms import OpenAI
# from langchain.chains import RetrievalQA
# from pinecone import Pinecone, ServerlessSpec
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Pinecone
# pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            if file.name.endswith('.csv'):
                try:
                    # Read CSV file
                    df = pd.read_csv(file)
                    
                    # Convert to JSON
                    json_data = df.to_json(orient='records')
                    qa_pairs = json.loads(json_data)
                    
                    # Save to database
                    for pair in qa_pairs:
                        QAPair.objects.create(question=pair['question'], answer=pair['answer'])
                    
                    # Save to Pinecone
                    # save_to_pinecone(qa_pairs)
                    
                    messages.success(request, 'File uploaded, processed, and saved to Pinecone successfully.')
                    return redirect('qa_app:upload_document')
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
                    messages.error(request, f'Error processing file: {str(e)}')
            else:
                messages.error(request, 'Please upload a CSV file.')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'qa_app/upload_document.html', {'form': form})

# def save_to_pinecone(qa_pairs):
#     try:
#         # Initialize OpenAI embeddings
#         embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
#         # Initialize Pinecone vector store
#         index_name = "pined"
#         if index_name not in pc.list_indexes().names():
#             pc.create_index(
#                 name=index_name,
#                 dimension=5000,  # OpenAI embeddings are 1536 dimensions
#                 metric='cosine',
#                 spec=ServerlessSpec(
#                     cloud='aws',
#                     region='us-east-1'  # Replace with your preferred region
#                 )
#             )
        
#         index = pc.Index(index_name)
        
#         # Prepare data for Pinecone
#         texts = [f"Q: {pair['question']}\nA: {pair['answer']}" for pair in qa_pairs]
#         embeddings_list = embeddings.embed_documents(texts)
        
#         # Add to Pinecone
#         vectors = [(f"qa_{i}", embedding, {"text": text}) for i, (text, embedding) in enumerate(zip(texts, embeddings_list))]
#         index.upsert(vectors=vectors)
        
#         logger.info(f"Successfully added {len(texts)} Q&A pairs to Pinecone")
#     except Exception as e:
#         logger.error(f"Error saving to Pinecone: {str(e)}")
#         raise

