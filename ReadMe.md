# Paul Graham Essays RAG System

A Retrieval-Augmented Generation (RAG) system that allows you to query and interact with Paul Graham's essays using natural language. This system combines web scraping, text embedding, and OpenAI's language models to provide intelligent responses based on Paul Graham's writings.

![RAG Output](https://github.com/hackice20/pg-rag/blob/main/rag-output.png?raw=true)

## Components

### 1. Scraper (`scraper.py`)
- Scrapes essays from Paul Graham's website
- Extracts essay titles, content, and URLs
- Saves data in a structured format
- Includes error handling and logging

### 2. Embeddings Generator (`embeddings.py`)
- Processes scraped essays into chunks
- Generates embeddings using OpenAI's API
- Implements retry logic and error handling
- Saves embeddings for efficient retrieval

### 3. RAG System (`rag.py`)
- Provides a conversational interface to query the essays
- Uses embeddings for semantic search
- Generates context-aware responses
- Includes conversation history for better context

## Usage

1. **Scraping Essays**
```python
from scraper import scrape_essays
essays = scrape_essays()
```

2. **Generating Embeddings**
```python
from embeddings import generate_embeddings
embeddings = generate_embeddings(essays)
```

3. **Querying the RAG System**
```python
from rag import RAGSystem
rag = RAGSystem()
response = rag.query("What does Paul Graham say about startups?")
```

## Features

- **Intelligent Search**: Uses semantic search to find relevant essay content
- **Context-Aware Responses**: Maintains conversation history for better context
- **Error Handling**: Robust error handling and logging throughout
- **Chunking**: Efficiently processes long essays by breaking them into manageable chunks
- **Retry Logic**: Implements retry mechanisms for API calls

## Requirements

- Python 3.x
- OpenAI API key
- Required Python packages (see requirements.txt)

## Note

This system requires an OpenAI API key to function. Make sure to set your API key in the environment variables before running the system.
