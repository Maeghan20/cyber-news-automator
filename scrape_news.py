import feedparser
from supabase import create_client
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API keys
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini Pro (use free-tier model)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')  # Changed from 1.5-pro

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Scrape Google News
news_feed = feedparser.parse("https://news.google.com/rss/search?q=cybersecurity+when:1d&hl=en-US&gl=US&ceid=US:en")
articles = [{"title": entry.title, "link": entry.link} for entry in news_feed.entries[:5]]

# Save to database
try:
    supabase.table("news").insert(articles).execute()
except Exception as e:
    print(f"Supabase insert error: {str(e)}")

# Generate summary
prompt = f"""
Summarize these cybersecurity articles into a LinkedIn post:
{str(articles)}

- Use bullet points
- Add relevant emojis
- Include 3 hashtags
- Keep under 500 characters
"""

try:
    response = model.generate_content(prompt)
    summary = response.text
except Exception as e:
    summary = f"Error generating summary: {str(e)}"

# Save summary
try:
    supabase.table("summaries").insert({"content": summary, "is_approved": False}).execute()
    print("Success! Summary saved.")
except Exception as e:
    print(f"Supabase summary save error: {str(e)}")