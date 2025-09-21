"""Files for the twooter API interface"""

import twooter.sdk
from twooter import Twooter
import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


class TweeterClient:
    def __init__(self, account_provider):
        self.account_provider = account_provider
        """
        existence_check = tweeter.user_get(name)
        if not existence_check:
            raise 
        """

    async def _auto_like_and_retreat_with_all_accounts(
        self, post_id: int, posting_account_username: str
    ):
        """Helper method to auto-like and repost a post with all accounts except the posting account."""
        accounts = self.account_provider.get_all_accounts()
        logger.info(f"Starting auto-like/repost with {len(accounts)} accounts...")

        loop = asyncio.get_event_loop()
        tasks = []

        for i, tweeter_bot in enumerate(accounts):
            try:
                bot_info = tweeter_bot.user_me()
                bot_username = bot_info["data"]["username"]

                # Always like
                logger.info(f"Account #{i + 1} ({bot_username}) - QUEUED for like")
                like_task = asyncio.wait_for(
                    loop.run_in_executor(None, functools.partial(tweeter_bot.post_like, post_id)),
                    timeout=10.0,
                )
                tasks.append((i, bot_username, "like", like_task))

                # Repost only if not the posting account
                if bot_username != posting_account_username:
                    logger.info(f"Account #{i + 1} ({bot_username}) - QUEUED for repost")
                    repost_task = asyncio.wait_for(
                        loop.run_in_executor(None, functools.partial(tweeter_bot.post_repost, post_id)),
                        timeout=10.0,
                    )
                    tasks.append((i, bot_username, "repost", repost_task))

            except Exception as e:
                logger.error(f"Failed to get info for account #{i + 1}: {e}")

        # Run all the tasks concurrently
        results = await asyncio.gather(*(t[3] for t in tasks), return_exceptions=True)
        return results


        # Execute all likes and track results
        if tasks:
            like_results = await asyncio.gather(
                *[task for _, _, task in tasks], return_exceptions=True
            )

            # Log results for each account
            successful_likes = 0
            for (i, username, _), result in zip(tasks, like_results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Account #{i + 1} ({username}) FAILED to like post {post_id}: {result}"
                    )
                else:
                    logger.info(
                        f"Account #{i + 1} ({username}) SUCCESSFULLY liked post {post_id}"
                    )
                    successful_likes += 1

            logger.info(
                f"Auto-like complete: {successful_likes}/{len(tasks)} eligible accounts liked post {post_id}"
            )
            logger.info(
                f"Expected likes on website: {successful_likes} (including self-like)"
            )
            return successful_likes
        else:
            logger.warning(
                "No eligible accounts for auto-liking (all accounts filtered out)"
            )
            return 0
        


    async def make_post(self, post: str) -> int:
        tweeter = self.account_provider.get_account()  # handles login and rotation
        print(tweeter.user_me())
        try:
            logger.info(
                f"Attempting to post ({len(post)} chars): {post[:100]}{'...' if len(post) > 100 else ''}"
            )

            # Wrap the synchronous SDK calls with timeout
            loop = asyncio.get_event_loop()

            # Post with timeout (15 seconds)
            post_func = functools.partial(tweeter.post, post)

            response = await asyncio.wait_for(
                loop.run_in_executor(None, post_func), timeout=15.0
            )

            post_id = response["data"]["id"]
            logger.info(f"Post successful! Post ID: {post_id}")

            # Get posting account info for auto-like logic
            posting_account_info = tweeter.user_me()
            posting_username = posting_account_info["data"]["username"]
            logger.info(f"Post created by account: {posting_username}")

            # Auto-like with all accounts using helper method
            await self._auto_like_and_retreat_with_all_accounts(post_id, posting_username)

            return post_id

        except asyncio.TimeoutError:
            logger.error("Post request timed out after 15 seconds")
            raise Exception("Post request timed out - server may be slow")
        except Exception as e:
            logger.error(f"Failed to post: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            raise

    async def send_reply(self, reply: str, post_id):
        """Sends a reply to a post"""
        logger.info(
            f"Attempting to reply ({len(reply)} chars): {reply[:100]}{'...' if len(reply) > 100 else ''}"
        )
        try:
            tweeter: Twooter = self.account_provider.get_account()
            print("sending a reply")

            loop = asyncio.get_event_loop()

            # Post reply with timeout (15 seconds)
            post_func = functools.partial(tweeter.post, reply, parent_id=post_id)
            response = await asyncio.wait_for(
                loop.run_in_executor(None, post_func), timeout=15.0
            )

            reply_id = response["data"]["id"]
            logger.info(f"Reply successful! Reply ID: {reply_id}")

            # Get replying account info for auto-like logic
            replying_account_info = tweeter.user_me()
            replying_username = replying_account_info["data"]["username"]
            logger.info(f"Reply created by account: {replying_username}")

            # Auto-like the reply with all accounts using helper method
            try:
                await self._auto_like_and_retreat_with_all_accounts(reply_id, replying_username)
            except:
                logger.error(f"Failed to auto like with all accounts, continuing")

            return reply_id

        except Exception as e:
            logger.error(f"Failed to post: {e}")
            if hasattr(e, "response"):
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
