# import logging
import re
import inspect
from copy import deepcopy
from typing import Mapping, OrderedDict

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem
from instapy import InstaPy, smart_run

# from instapy import smart_run

ACTIONS_LIST = []

# provide not documented descriptions
_INSTA_ACTIONS_DESCRIPTIONS = {
    '__init__': 'Create main InstaPy object',
    'follow_by_tags': 'Follow user based on hashtags (without liking the image)',
    'follow_by_locations': 'This method allows following by locations, without liking or commenting posts.',
    'set_skip_users': 'This will skip all users that have one these keywords on their bio.',
    'set_delimit_commenting': 'Commenting based on the number of existing comments a post has',
    'set_delimit_liking': 'This is used to check the number of existing likes a post has and if it either exceed the '
                          'maximum value set OR does not pass the minimum value set then it will not like that post',
}


# def InstaAction3(class_of_function: type, func_name: str):
#     res = QListWidgetItem()
#     res.setText(func_name)
#
#     return res


class InstaAction:
    """
    call


    import foo
    method_to_call = getattr(foo, 'bar')
    result = method_to_call()

    You could shorten lines 2 and 3 to:

    result = getattr(foo, 'bar')()
    """
    class_of_function = None

    name = ''
    decsription = ''

    # command: str = ''
    # caption: str = ''
    anotation_call: Mapping[str, inspect.Parameter] = {}

    # annotation_return: type = None

    def __init__(self, class_of_function: type, func_name: str):
        super().__init__()
        self.class_of_function = class_of_function
        self.call_func = getattr(class_of_function, func_name)
        self.name = func_name
        # self.setText(self.name)

        self.decsription = re.sub(' +', ' ', (
            self.call_func.__doc__.replace('\n', ' ').strip())) \
            if self.call_func.__doc__ \
            else _INSTA_ACTIONS_DESCRIPTIONS.get(func_name, "[ ********* UNKNOWN DESCRIPTION ******** ]")
        # _ = inspect.signature(self.call_func).parameters
        self.anotation_call = OrderedDict(inspect.signature(self.call_func).parameters)  # noqa

        self.values = {}

        # self.annotation_return = inspect.signature(self.call_func).return_annotation
        pass

    def __repr__(self):
        return f'[{self.class_of_function}] {self.name}'


# InstaPyStageItem = GetStartStage()


def add_actions(action_list: list, cls, except_list: list):
    # QListWidgetItem
    _list = [InstaAction(class_of_function=cls, func_name=x)
             for x in dir(cls)
             if not x.startswith('_')
             and callable(getattr(cls, x))
             and x not in except_list]

    for item in _list:
        _el2 = QListWidgetItem()
        _el2.setText(item.name)
        _el2.object = item

        action_list.append(_el2)


def add_actions2(action_list: list, cls, except_list: list):
    action_list.extend([InstaAction(class_of_function=cls, func_name=x)
                        for x in dir(cls)
                        if not x.startswith('_')
                        and callable(getattr(cls, x))
                        and x not in except_list])


# add_actions(ACTIONS_LIST, InstaPy,
#             ['end', 'check_character_set', 'engage_with_posts', 'fetch_smart_comments', 'interact_user_following',
#              'is_mandatory_character'])

# ACTIONS_LIST.append(InstaAction('InstaPy'))


add_actions(ACTIONS_LIST, InstaPy,
            ['end', 'set_mandatory_language', 'check_character_set', 'engage_with_posts', 'fetch_smart_comments',
             'interact_user_following', 'is_mandatory_character', 'set_do_like', 'set_sleep_reduce', 'set_switch_language'])
# add_actions(ACTIONS_LIST, InstaPy, ['end', ])
pass


def get_actions_list_old():
    return ACTIONS_LIST


def get_actions_list():
    # res = [f'{x.class_of_function} {x.name} - {x.decsription}' for x in ACTIONS_LIST]
    max_len = max(len(x.object.name) for x in ACTIONS_LIST)
    res = [f'{x.object.name.ljust(max_len)} {x.object.decsription}' for x in ACTIONS_LIST]
    return res


def insta_clone(item):
    res = item.clone()
    res.object = deepcopy(item.object)
    return res


# start stage
_InstaPyStartStageItem = InstaAction(InstaPy, '__init__')
_el = QListWidgetItem()
_el.setText(_InstaPyStartStageItem.decsription)
_el.object = _InstaPyStartStageItem
InstaPyStartStageItem = _el

# end stage
_InstaPyStartStageItem = InstaAction(InstaPy, 'end')
_el = QListWidgetItem()
_el.setText(_InstaPyStartStageItem.decsription)
_el.object = _InstaPyStartStageItem
InstaPyEndStageItem = _el


# if __name__ == '__main__':
#     e = get_insta_actions_list()
#     print(e)
#     pass


class ExecuteScenario(QThread):
    idx = 1
    session = None

    # sig_step = pyqtSignal(int, str)  # worker id, step description: emitted every step through work() loop
    sig_done = pyqtSignal(int)  # worker id: emitted at end of work()

    # sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self, stages, instapy_start_values):
        QThread.__init__(self)
        self.stages = stages
        self.instapy_start_values = instapy_start_values

    def stop(self):
        if self.session:
            self.session.end()
        self.terminate()
        self.sig_done.emit(self.idx)

    # def __del__(self):
    #     self.wait()

    # def execute_scenario(stages, instapy_start_values):
    def run(self):

        # logging.info('Start working')
        self.session = InstaPy(**self.instapy_start_values)  # noqa

        with smart_run(self.session, threaded=True):
            # with smart_run(session):
            # Available character sets: LATIN, GREEK, CYRILLIC, ARABIC, HEBREW, CJK, HANGUL, HIRAGANA, KATAKANA and THAI
            self.session.set_mandatory_language(enabled=True, character_set=['LATIN', 'CYRILLIC'])

            for index, stage in enumerate(self.stages):
                # current_values = deepcopy(stage.values)

                # skip init and end stages
                if index == 0 or index == len(self.stages) - 1:
                    continue

                # convert text (valid for propretry editor) to list
                current_values = {
                    key: value.split() if stage.anotation_call[key].annotation.__name__ == 'list' else value for
                    (key, value) in stage.values.items()}

                # call function from instance
                f = getattr(self.session, stage.name)
                f(**current_values)  # noqa https://youtrack.jetbrains.com/issue/PY-27935

                # self.emit(SIGNAL('add_post(QString)'), top_post)
                # self.sig_step.emit(idx, )
                self.sleep(2)
                pass

        self.sig_done.emit(self.idx)

        # x = stages[len(stages)].value
        # insta.end()

        # ------------------------
        # if gecko_driver_path:
        #     shutil.rmtree(gecko_driver_path)
        # --------------------------------------------
        pass
        # logging.info('End working')
