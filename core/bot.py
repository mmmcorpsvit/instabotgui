import re

from instapy import InstaPy
from instapy import smart_run

# provide not documented descriptions
INSTA_ACTIONS_DESCRIPTIONS = {
    'follow_by_tags': 'Follow user based on hashtags (without liking the image)',
    'follow_by_locations': 'This method allows following by locations, without liking or commenting posts.',
    'set_skip_users': 'This will skip all users that have one these keywords on their bio.',
}


class InstaAction:
    func = None

    # command: str = ''
    # caption: str = ''
    # params: dict = {}

    def __init__(self, func):
        self.func = func

    # def __init__(self, command: str, caption: str, params: dict):
    #     self.command = command
    #     self.caption = caption
    #     self.params = params

    def __str__(self):
        function_name = self.func.__name__

        res = f'[{function_name}] **** Not Provide description ***'
        if self.func.__doc__:
            desc = re.sub(' +', ' ', (self.func.__doc__.strip()))

            if desc:
                res = f'[{function_name}] {desc}'
        else:

            res = f'[{function_name}] {INSTA_ACTIONS_DESCRIPTIONS.get(function_name, "[ UNKNOWN DESCRIPTION ]")}'

        return res


INSTA_ACTIONS: [InstaAction] = [
    InstaAction(InstaPy.like_by_tags),
    InstaAction(InstaPy.like_by_feed),
    InstaAction(InstaPy.like_by_locations),

    InstaAction(InstaPy.comment_by_locations),

    InstaAction(InstaPy.follow_by_tags),
    InstaAction(InstaPy.follow_by_locations),
    InstaAction(InstaPy.follow_by_list),
    InstaAction(InstaPy.follow_user_followers),
    InstaAction(InstaPy.follow_user_following),
    InstaAction(InstaPy.follow_likers),
    InstaAction(InstaPy.follow_commenters),
    InstaAction(InstaPy.unfollow_users),

    InstaAction(InstaPy.interact_by_URL),
    InstaAction(InstaPy.interact_by_comments),

    InstaAction(InstaPy.remove_follow_requests),

    InstaAction(InstaPy.set_skip_users),
    InstaAction(InstaPy.set_do_story),

    InstaAction(InstaPy.story_by_tags),
    InstaAction(InstaPy.story_by_users),
]


def get_insta_actions_list():
    res = [str(x) for x in INSTA_ACTIONS]
    return res
