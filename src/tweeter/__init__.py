"""Files for the twooter API interface"""
import twooter.sdk
import asyncio
import functools

class TweeterClient:
    def __init__(self, name: str, password: str, display_name: str):
        self.name = name
        self.password = password
        self.display_name = display_name

        tweeter = twooter.sdk.new()
        tweeter.login(name, password, display_name=display_name)
        self.tweeter = tweeter

        """
        existence_check = tweeter.user_get(name)
        if not existence_check:
            raise 
        """

    async def make_post(self, post: str):
        try:
            print(f"Attempting to post: {post[:50]}...")
            
            # Wrap the synchronous post call with timeout
            loop = asyncio.get_event_loop()
            post_func = functools.partial(self.tweeter.post, post)
            
            # 15 second timeout for posting
            response = await asyncio.wait_for(
                loop.run_in_executor(None, post_func), 
                timeout=15.0
            )
            
            print(f"Post response: {response}")
            post_id = response["data"]["id"]
            
            # Also wrap the like call with timeout
            like_func = functools.partial(self.tweeter.post_like, post_id)
            await asyncio.wait_for(
                loop.run_in_executor(None, like_func),
                timeout=10.0
            )
            
            return post_id
        except asyncio.TimeoutError:
            print("Error: Post request timed out")
            raise Exception("Post request timed out - server may be slow or unreachable")
        except Exception as e:
            print(f"Error making post: {e}")
            print(f"Error type: {type(e)}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
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
t.login("Tristan", "dargem12931", display_name="Tristan")

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