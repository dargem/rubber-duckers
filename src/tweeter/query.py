"""A query agent for the new, other people trending topics etc"""
import twooter.sdk
import requests
from typing import List
from bs4 import BeautifulSoup
import random

class QueryAgent:
    def __init__(self, name: str, password: str, display_name: str):
        self.name = name
        self.password = password
        self.display_name = display_name

        tweeter = twooter.sdk.new()
        tweeter.login(name, password, display_name=display_name)
        self.query = tweeter

    def get_trending(self):
        self.query.feed("trending")

    def get_random_news_article(self) -> str:
        site_url = 'https://kingston-herald.legitreal.com'
        url = 'https://kingston-herald.legitreal.com/index.html'
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')  # Use built-in parser instead of lxml

        # Find all <a> tags where the href attribute starts with "/post"
        post_links = soup.select('a[href^="/post"]')
        # Then append it so it gets the full uri not just rel path from website
        post_links = [site_url + link.get('href') for link in post_links]

        chosen_link_index = random.randint(0,len(post_links)-1)
        link = post_links[chosen_link_index]

        print(link)
        # Get the content of each article page
        article_response = requests.get(link)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        paragraphs = article_soup.select('p')
        article = ""
        for paragraph in paragraphs:
            article += "\n" + paragraph.get_text()
        
        return article

    def get_news(self) -> List[str]:
        site_url = 'https://kingston-herald.legitreal.com'
        url = 'https://kingston-herald.legitreal.com/index.html'
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')  # Use built-in parser instead of lxml
        articles = []

        # Find all <a> tags where the href attribute starts with "/post"
        post_links = soup.select('a[href^="/post"]')
        # Then append it so it gets the full uri not just path
        post_links = [site_url + link.get('href') for link in post_links]

        for link in post_links:
            print(link)
            # Get the content of each article page
            article_response = requests.get(link)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            paragraphs = article_soup.select('p')
            article = ""
            for paragraph in paragraphs:
                article += "\n" + paragraph.get_text()
            articles.append(article.strip())
        
        return articles


            

        



"""
Barebones implementation for now
import twooter.sdk

def repost_or_unrepost(t, post_id: int):
    try:
        t.post_repost(post_id)
    except Exception as e:
        sc = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)
        if sc == 409:
            t.post_unrepost(post_id)
        else:
            raise

t = twooter.sdk.new()

print(t.user_get("Tristan"))
t.user_me()
t.user_update_me("Tristan", "I used the SDK to change this!")
t.user_activity("Tristan")
t.user_follow("admin")
t.user_unfollow("admin")

post_id = t.post("Hello, world! 123123123 @Tristan")["data"]["id"]
print(t.search("Hello, world! 123123123 @Tristan"))
#t.post_delete(post_id)
print(t.search("Hello, world! 123123123 @Tristan"))

t.notifications_list()
t.notifications_unread()
t.notifications_count()
t.notifications_count_unread()

t.feed("trending")
t.feed("home", top_n=1)

t.post_like(post_id)
#repost_or_unrepost(t, 123)
print(t.post_get(post_id))
print(t.post_replies(post_id))

t.logout()
"""