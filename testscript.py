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