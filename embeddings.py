import os
import json
import openai
import time
from dotenv import load_dotenv
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

def chunk_text(text, max_chunk_size=8000):
    """Split text into chunks of max_chunk_size characters"""
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < max_chunk_size:
            current_chunk += paragraph + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def create_embedding_with_retry(text, max_retries=3):
    """Create embedding with retry logic"""
    for attempt in range(max_retries):
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            if 'data' in response and len(response['data']) > 0:
                return response['data'][0]['embedding']
            else:
                print(f"Invalid response format, attempt {attempt + 1}/{max_retries}")
        except Exception as e:
            print(f"Error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
    return None

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

def create_embeddings():
    """Create embeddings for essays in paul_essays.json"""
    # Check if essays file exists
    if not os.path.exists('paul_essays.json'):
        print("Error: paul_essays.json not found. Please run scraper.py first.")
        return False

    # Load essays
    print("Loading essays from paul_essays.json...")
    with open('paul_essays.json', 'r') as f:
        essays = json.load(f)
    
    if not essays:
        print("Error: No essays found in paul_essays.json")
        return False
    
    print(f"Loaded {len(essays)} essays")
    
    # Create embeddings
    embeddings = []
    print("\nCreating embeddings...")
    
    try:
        for essay in tqdm(essays, desc="Processing essays"):
            try:
                # Split essay into chunks if needed
                chunks = chunk_text(essay['content'])
                chunk_embeddings = []
                
                for chunk in chunks:
                    embedding = create_embedding_with_retry(chunk)
                    if embedding:
                        chunk_embeddings.append(embedding)
                    else:
                        print(f"Failed to create embedding for chunk in: {essay['title']}")
                        continue
                
                if chunk_embeddings:
                    # Average the embeddings if there are multiple chunks
                    avg_embedding = [sum(x) / len(x) for x in zip(*chunk_embeddings)]
                    embeddings.append({
                        'title': essay['title'],
                        'url': essay['url'],
                        'content': essay['content'],
                        'embedding': avg_embedding
                    })
                    print(f"Created embedding for: {essay['title']}")
                else:
                    print(f"Warning: No valid embeddings created for: {essay['title']}")
                    
            except Exception as e:
                print(f"Error processing essay {essay['title']}: {str(e)}")
                continue
        
        if not embeddings:
            print("Error: No embeddings were created!")
            return False
            
        # Save embeddings to JSON
        print("\nSaving embeddings to paul_essays_embeddings.json...")
        with open('paul_essays_embeddings.json', 'w') as f:
            json.dump(embeddings, f, indent=2)
        print(f"Successfully saved {len(embeddings)} embeddings")
        
        return True
        
    except Exception as e:
        print(f"Error in embedding creation: {str(e)}")
        return False

def main():
    print("Starting embedding creation process...")
    
    # Test OpenAI connection
    if not test_openai_connection():
        print("Exiting due to OpenAI API connection failure")
        return
    
    # Create embeddings
    if create_embeddings():
        print("\nEmbedding creation completed successfully!")
    else:
        print("\nEmbedding creation failed!")

if __name__ == "__main__":
    main() 