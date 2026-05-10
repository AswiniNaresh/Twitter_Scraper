import streamlit as st
from src.scraper import TwitterScraper
from src.database import MongoDBHandler
from src.utils import create_dataframe, export_to_csv, export_to_json
from config import MONGO_URI, MAX_TWEETS, DEFAULT_TWEET_LIMIT
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(page_title="Twitter Data Scraper", layout="wide")
    
    st.title("Twitter Data Scraper")
    st.markdown("""
    Search and collect Twitter data based on keywords or hashtags.
    Data can be saved to MongoDB and exported in CSV or JSON format.
    """)

    # Initialize components
    scraper = TwitterScraper()
    db_handler = MongoDBHandler(MONGO_URI)

    # User input form
    with st.form("scraping_form"):
        col1, col2 = st.columns(2)
        with col1:
            keyword = st.text_input("Enter Keyword or Hashtag:")
            tweet_limit = st.number_input(
                "Number of Tweets:", 
                min_value=1,
                max_value=MAX_TWEETS,
                value=DEFAULT_TWEET_LIMIT
            )
        with col2:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        submit_button = st.form_submit_button("Scrape Tweets")

    if submit_button:
        if not keyword:
            st.error("Please enter a keyword or hashtag.")
            return

        try:
            with st.spinner("Scraping tweets..."):
                tweets = scraper.scrape_tweets(
                    keyword,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    tweet_limit
                )

            if tweets:
                df = create_dataframe(tweets)
                st.success(f"Successfully scraped {len(tweets)} tweets!")
                st.dataframe(df)

                # Export options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Save to MongoDB"):
                        if db_handler.save_tweets(keyword, tweets):
                            st.success("Saved to MongoDB!")
                        else:
                            st.error("Failed to save to MongoDB.")
                
                with col2:
                    csv_data = export_to_csv(df)
                    st.download_button(
                        "Download CSV",
                        csv_data,
                        "tweets.csv",
                        "text/csv"
                    )
                
                with col3:
                    json_data = export_to_json(tweets)
                    st.download_button(
                        "Download JSON",
                        json_data,
                        "tweets.json",
                        "application/json"
                    )

        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Scraping error: {str(e)}")

if __name__ == "__main__":
    main()