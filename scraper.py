import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_paul_essays():
    """Scrape Paul Graham's essays from his website."""
    base_url = "http://www.paulgraham.com/articles.html"
    print("Fetching articles page...")
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("HTML content length:", len(response.text))
        
        essays = []
        # Find all essay links - Paul Graham's site uses a table for articles
        table = soup.find('table')
        if not table:
            print("Error: Could not find articles table")
            return []
            
        print("Found articles table, searching for essays...")
        for row in table.find_all('tr'):
            link = row.find('a')
            if link and link.get('href') and link['href'].endswith('.html'):
                essay_url = f"http://www.paulgraham.com/{link['href']}"
                essay_title = link.text.strip()
                print(f"\nProcessing essay: {essay_title}")
                
                try:
                    # Get essay content
                    print(f"Fetching content from: {essay_url}")
                    essay_response = requests.get(essay_url)
                    essay_response.raise_for_status()
                    essay_soup = BeautifulSoup(essay_response.text, 'html.parser')
                    
                    # Extract the main content - Paul Graham's essays are in a table
                    content_table = essay_soup.find('table')
                    if content_table:
                        essay_text = content_table.get_text(separator='\n', strip=True)
                        if len(essay_text) > 100:  # Basic validation
                            essays.append({
                                'title': essay_title,
                                'url': essay_url,
                                'content': essay_text
                            })
                            print(f"Successfully scraped: {essay_title} ({len(essay_text)} chars)")
                        else:
                            print(f"Warning: Content too short for {essay_title}")
                    else:
                        print(f"Error: Could not find content table for {essay_title}")
                    
                    # Be nice to the server
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing {essay_title}: {str(e)}")
                    continue
        
        print(f"\nTotal essays scraped: {len(essays)}")
        if len(essays) == 0:
            print("Warning: No essays were scraped!")
            return []
            
        # Save to JSON
        with open('paul_essays.json', 'w') as f:
            json.dump(essays, f, indent=2)
        print("Saved essays to paul_essays.json")
        
        return essays
        
    except Exception as e:
        print(f"Error in scraping: {str(e)}")
        return []

if __name__ == "__main__":
    print("Starting Paul Graham essay scraper...")
    essays = scrape_paul_essays()
    print(f"Scraping complete. Found {len(essays)} essays.") 