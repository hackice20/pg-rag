import os
import json
import openai
from dotenv import load_dotenv
import numpy as np
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Verify API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# Set OpenAI API key
openai.api_key = api_key

def test_openai_connection():
    """Test if OpenAI API is working"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        print("OpenAI API connection successful!")
        return True
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return False

def semantic_search(query, embeddings, top_k=3):
    """Perform semantic search using cosine similarity."""
    if not embeddings:
        print("Error: No embeddings available for search")
        return []
        
    try:
        # Get query embedding
        response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002"
        )
        
        if 'data' not in response or len(response['data']) == 0:
            print("Error: Invalid response format for query embedding")
            return []
            
        query_embedding = response['data'][0]['embedding']
        
        # Calculate cosine similarity
        similarities = []
        for essay in embeddings:
            try:
                similarity = np.dot(query_embedding, essay['embedding']) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(essay['embedding'])
                )
                similarities.append((similarity, essay))
            except Exception as e:
                print(f"Error calculating similarity: {str(e)}")
                continue
        
        # Sort by similarity and get top k results
        similarities.sort(reverse=True)
        return similarities[:top_k]
    except Exception as e:
        print(f"Error in semantic search: {str(e)}")
        return []

def get_rag_response(query, relevant_essays):
    """Get response from GPT using relevant essays as context."""
    if not relevant_essays:
        return "Sorry, I couldn't find any relevant essays to answer your question."
        
    try:
        # Prepare context from relevant essays
        context = "\n\n".join([
            f"Title: {essay['title']}\nContent: {essay['content'][:1000]}..."
            for _, essay in relevant_essays
        ])
        
        # Create prompt
        prompt = f"""Based on the following context from Paul Graham's essays, answer the question.
        
Context:
{context}

Question: {query}

Answer:"""
        
        # Get response from GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on Paul Graham's essays."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            return "Error: Invalid response format from GPT"
    except Exception as e:
        print(f"Error getting RAG response: {str(e)}")
        return "Sorry, I encountered an error while trying to answer your question."

def main():
    # Test OpenAI connection first
    if not test_openai_connection():
        print("Exiting due to OpenAI API connection failure")
        return
        
    # Check if we have embeddings
    if not os.path.exists('paul_essays_embeddings.json'):
        print("Error: paul_essays_embeddings.json not found. Please run embeddings.py first.")
        return
        
    # Load embeddings
    print("Loading embeddings...")
    with open('paul_essays_embeddings.json', 'r') as f:
        embeddings = json.load(f)
    print(f"Loaded {len(embeddings)} embeddings")
    
    print("\nPaul Graham RAG System")
    print("Type 'quit' to exit")
    
    try:
        while True:
            try:
                query = input("\nEnter your question: ").strip()
                if not query:
                    continue
                    
                if query.lower() == 'quit':
                    print("Goodbye!")
                    break
                
                # Get relevant essays
                relevant_essays = semantic_search(query, embeddings)
                if not relevant_essays:
                    print("No relevant essays found")
                    continue
                
                # Get and print response
                response = get_rag_response(query, relevant_essays)
                print("\nResponse:", response)
                
                # Print sources
                print("\nSources:")
                for _, essay in relevant_essays:
                    print(f"- {essay['title']}: {essay['url']}")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled. Type 'quit' to exit or continue with a new question.")
                continue
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 