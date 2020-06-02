import re

from instapy import InstaPy

# from instapy import smart_run

ACTIONS_LIST = []

# provide not documented descriptions
_INSTA_ACTIONS_DESCRIPTIONS = {
    'follow_by_tags': 'Follow user based on hashtags (without liking the image)',
    'follow_by_locations': 'This method allows following by locations, without liking or commenting posts.',
    'set_skip_users': 'This will skip all users that have one these keywords on their bio.',
}


class InstaAction:
    """
    call


    import foo
    method_to_call = getattr(foo, 'bar')
    result = method_to_call()

    You could shorten lines 2 and 3 to:

    result = getattr(foo, 'bar')()
    """
    function_name = None
    class_of_function = None

    name = ''
    decsription = ''

    # command: str = ''
    # caption: str = ''
    params: dict = {}

    def __init__(self, class_of_function: type, func_name: str, ):
        self.class_of_function = class_of_function
        self.call_func = getattr(class_of_function, func_name)
        self.name = func_name

        self.decsription = re.sub(' +', ' ', (
            self.call_func.__doc__.strip())) \
            if self.call_func.__doc__ \
            else _INSTA_ACTIONS_DESCRIPTIONS.get(self.function_name, "[ UNKNOWN DESCRIPTION ]")
        self.params = {}

    def __repr__(self):
        return f'[{self.class_of_function}] {self.name}'


def add_actions(action_list: list, cls, except_list: list):
    action_list.extend([InstaAction(class_of_function=cls, func_name=x)
                        for x in dir(cls)
                        if not x.startswith('_')
                        and callable(getattr(cls, x))
                        and x not in except_list])


add_actions(ACTIONS_LIST, InstaPy, [])
pass


# from optparse import OptionParser
# import inspect


def get_insta_actions_list():
    # except_methods = ['end']
    # r = 'fgh'
    # # r.startswith('_')
    # x = inspect.getmembers(InstaPy, predicate=inspect.isclass)
    # y = [x for x in dir(InstaPy) if not x.startswith('_') and not x in except_methods]
    res = [f'{x.class_of_function} {x.name} - {x.decsription}' for x in ACTIONS_LIST]
    # res = [f'{x.name} {x.decsription}' for x in ACTIONS_LIST]

    # res.insert(0, INSTA_MAIN_ACTION)
    return res


if __name__ == '__main__':
    e = get_insta_actions_list()
    print(e)
    pass
