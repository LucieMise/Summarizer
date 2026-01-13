import torch
from transformers import pipeline
import requests
from bs4 import BeautifulSoup


def fetch_text_from_url(url):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    for tags in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        tags.decompose()

    text = " ".join(p.get_text() for p in soup.find_all("p"))
    return text

def chunk_text(text, max_words=300,min_words=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
         chunk = " ".join(words[i:i + max_words])
         if len(chunk.split()) > min_words:
            chunks.append(chunk)
    return chunks

def summarize_text(text):

    chunks = chunk_text(text)
    summaries = []
    summarizer = pipeline(
         "summarization", 
         model="facebook/bart-large-cnn",
         device=0 if torch.cuda.is_available() else -1
         )
    

    for chunk in chunks:
        summary = summarizer(
            chunk, 
            max_length=130, 
            min_length=30, 
            do_sample=False
            )
        
        summaries.append(summary[0]["summary_text"])
            
    if not summaries:
        return "Text too short to summarize effectively."
        
    combined_summary = "".join(summaries)

    if len(chunks) > 1:
        final_summary = summarizer(
            combined_summary,
            max_length=150,
            min_length=30,
            do_sample=False
        )[0]["summary_text"]
        return final_summary
    else:
        return combined_summary
    
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"  # example URL
    print("Fetching article...")
    article_text = fetch_text_from_url(url)
    print("Article fetched. Summarizing...")
    summary = summarize_text(article_text)
    print("\nSUMMARY:\n")
    print(summary)