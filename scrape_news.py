import feedparser
from supabase import create_client
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Free tier: 60 req/min

# Initialize Gemini Pro
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Step 1: Scrape Google News
news_feed = feedparser.parse("https://news.google.com/rss/search?q=cybersecurity+when:1d&hl=en-US&gl=US&ceid=US:en")
articles = [{"title": entry.title, "link": entry.link} for entry in news_feed.entries[:5]]  # Top 5

# Save to Supabase
supabase.table("news").insert(articles).execute()

# Step 2: Generate Summary with Gemini Pro
prompt = f"""
You are a cybersecurity expert. Summarize key developments from these articles into bullet points. Add emojis and hashtags:
{articles}

- Use bullet points
- Add relevant emojis
- Include 3 hashtags
"""

try:
    response = model.generate_content(prompt)
    summary = response.text
except Exception as e:
    summary = f"Error generating summary: {str(e)}"

# Save summary to database
supabase.table("summaries").insert({"content": summary, "is_approved": False}).execute()
print("Success! Summary saved.")