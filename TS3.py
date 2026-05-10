import streamlit as st
from PIL import Image
import pandas as pd
import snscrape.modules.twitter as sntwitter
import base64
from datetime import datetime
import time
import ssl
import certifi
import urllib3
import requests

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a custom SSL context
ssl_context = ssl.create_default_context()
#ssl_context.check_hostname = False
#ssl_context.verify_mode = ssl.CERT_NONE

def create_scraper():
    """Create a scraper instance with SSL verification disabled"""
    return sntwitter.TwitterSearchScraper('')

def scrape_twitter_data(keyword, start_date, end_date, tweet_limit):
    tweets = []
    progress_bar = st.progress(0)
    tweet_count = 0
    
    try:
        # Construct search query
        search_query = f"{keyword} since:{start_date} until:{end_date}"
        
        # Create scraper with SSL verification disabled
        scraper = sntwitter.TwitterSearchScraper(search_query)
        
        # Modify scraper's session to disable SSL verification
        if hasattr(scraper, '_session'):
            scraper._session.verify = False
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                for tweet in scraper.get_items():
                    if len(tweets) >= tweet_limit:
                        break
                    
                    tweets.append({
                        'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                        'id': tweet.id,
                        'content': tweet.rawContent,
                        'user': tweet.user.username,
                        'reply_count': tweet.replyCount,
                        'retweet_count': tweet.retweetCount,
                        'language': tweet.lang,
                        'like_count': tweet.likeCount,
                        'quote_count': tweet.quoteCount,
                        'view_count': tweet.viewCount if hasattr(tweet, 'viewCount') else 0,
                    })
                    
                    # Update progress
                    tweet_count += 1
                    progress = min(1.0, tweet_count / tweet_limit)
                    progress_bar.progress(progress)
                    
                    # Show status every 10 tweets
                    if tweet_count % 10 == 0:
                        st.info(f"Collected {tweet_count} tweets...")
                    
                    # Add delay between requests
                    time.sleep(0.5)
                
                break  # Break if successful
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    st.warning(f"Error occurred. Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    st.error(f"Failed after {max_retries} attempts. Error: {str(e)}")
                    return []
    
    except Exception as e:
        st.error(f"Error occurred while scraping: {str(e)}")
        return []
    
    return tweets

def main():
    st.title("Twitter Scraping with SSL Fix")
    
    # Try to load logo
    try:
        img = Image.open("Twitter-Logo-2010.png")
        st.image(img, width=450)
    except:
        st.write("Note: Logo image not found")
    
    # Input fields
    col1, col2 = st.columns(2)
    
    with col1:
        keyword = st.text_input("Enter keyword or hashtag:",
                              help="Enter search term (e.g., 'python' or '#python')")
    
    with col2:
        tweet_limit = st.number_input("Number of tweets to collect:",
                                    min_value=1,
                                    max_value=1000,
                                    value=100)
    
    col3, col4 = st.columns(2)
    
    with col3:
        start_date = st.date_input("Start date")
        start_date = start_date.strftime('%Y-%m-%d')
    
    with col4:
        end_date = st.date_input("End date")
        end_date = end_date.strftime('%Y-%m-%d')
    
    # Advanced options in expander
    with st.expander("Advanced Options"):
        exclude_retweets = st.checkbox("Exclude retweets")
        min_likes = st.number_input("Minimum likes:", min_value=0, value=0)
        verified_only = st.checkbox("Verified accounts only")
    
    if st.button("Start Scraping"):
        if not keyword:
            st.error("Please enter a keyword or hashtag!")
            return
        
        # Build search query with filters
        search_query = keyword
        if exclude_retweets:
            search_query += " -filter:retweets"
        if verified_only:
            search_query += " filter:verified"
        if min_likes > 0:
            search_query += f" min_likes:{min_likes}"
        
        with st.spinner('Scraping tweets...'):
            scraped_data = scrape_twitter_data(search_query, start_date, end_date, tweet_limit)
            
            if scraped_data:
                df = pd.DataFrame(scraped_data)
                
                # Display data
                st.subheader(f"Collected {len(df)} tweets")
                st.dataframe(df)
                
                # Download options
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Download as CSV"):
                        csv = df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="twitter_data.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success("CSV file ready for download!")
                
                with col2:
                    if st.button("Download as JSON"):
                        json_str = df.to_json(orient='records')
                        b64 = base64.b64encode(json_str.encode()).decode()
                        href = f'<a href="data:file/json;base64,{b64}" download="twitter_data.json">Download JSON File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success("JSON file ready for download!")
            else:
                st.error("No tweets found for the given criteria.")

if __name__ == '__main__':
    main()