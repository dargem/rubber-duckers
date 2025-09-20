"""Files for the twooter API interface"""
import twooter.sdk
import asyncio
import functools
import logging

logger = logging.getLogger(__name__)

class TweeterClient:
    def __init__(self, name: str, password: str, display_name: str, member_email: str):
        self.name = name
        self.password = password
        self.display_name = display_name
        self.member_email = member_email

        tweeter = twooter.sdk.new()
        tweeter.login(name, password, display_name=display_name, member_email=member_email)
        self.tweeter = tweeter

        """
        existence_check = tweeter.user_get(name)
        if not existence_check:
            raise 
        """

    async def make_post(self, post: str):
        try:
            logger.info(f"Attempting to post ({len(post)} chars): {post[:100]}{'...' if len(post) > 100 else ''}")
            
            # Wrap the synchronous SDK calls with timeout
            loop = asyncio.get_event_loop()
            
            # Post with timeout (15 seconds)
            post_func = functools.partial(self.tweeter.post, post)
            
            response = await asyncio.wait_for(
                loop.run_in_executor(None, post_func), 
                timeout=15.0
            )
            
            post_id = response["data"]["id"]
            logger.info(f"Post successful! Post ID: {post_id}")
            
            # Like with timeout (10 seconds)
            like_func = functools.partial(self.tweeter.post_like, post_id)
            await asyncio.wait_for(
                loop.run_in_executor(None, like_func),
                timeout=10.0
            )
            
            logger.info(f"Auto-liked post {post_id}")
            return post_id
            
        except asyncio.TimeoutError:
            logger.error("Post request timed out after 15 seconds")
            raise Exception("Post request timed out - server may be slow")
        except Exception as e:
            logger.error(f"Failed to post: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            raise
         

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