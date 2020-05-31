# -*- coding: utf-8 -*-
import asyncio
import inspect
import threading
from threading import Thread
import warnings
import regex

PATTERN_PICTURE = regex.compile('^.*\.(jpg|png|gif)$', flags=regex.IGNORECASE)

def get_attributes(obj, no_private_attr=True):
    all_attr = dir(obj)

    # exclude callables
    all_attr = list(filter(
        lambda x: not callable(getattr(obj, x)),
        all_attr
    ))

    # exclude private attributes start with __ or _
    if no_private_attr:
        all_attr = list(filter(
            lambda x: not x.startswith('_'),
            all_attr
        ))
    return all_attr

def check_essentials(obj, **kwargs):
    if 'essentials' in dir(obj.__class__):
        essentials = obj.__class__.essentials
    else:
        essentials = set()
    if not essentials.issubset(set(kwargs.keys())):
        raise AttributeError(
            'essential attributes missed for {}'.format(
                obj.__class__
            )
        )

def set_attributes(obj, **kwargs):
    # check input attributes
    # assume this is the final which is not extendable
    all_possible_attr = get_attributes(obj)
    redundant_attr = set(kwargs.keys()) - set(all_possible_attr)
    if len(redundant_attr) > 0:
        raise AttributeError(
            'redundant attributes for {}'.format(
                obj.__class__
            )
        )
    for (k, v) in kwargs.items():
        setattr(obj, k, v)

def get_class_functions(task_modules):
    cls_func =  {}
    for m in task_modules:
        clsmembers = inspect.getmembers(m, inspect.isclass)
        cls_func.update(dict(clsmembers))
    return cls_func

# https://stackoverflow.com/questions/33000200/asyncio-wait-for-event-from-other-thread
class Event_ts(asyncio.Event):
    # TODO: clear() method
    def set(self):
        #FIXME: The _loop attribute is not documented as public api!
        self._loop.call_soon_threadsafe(super().set)

def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        warnings.warn(
            'loop is running in get_event_loop() in thread {}. '
            'Please make sure the new coro using this loop does not block the original '
            'loop. (no long-time running sync version process)'
            'Otherwise, wrap the parent funtion which called this one in a new thread '
            'to avoid conflict with current loop '.format(
                threading.currentThread().getName()
            )
        )
    return loop

def run_coroutine_in_new_thread(coro):
    def run_coro(loop, coro):
        asyncio.set_event_loop(loop)
        r = loop.run_until_complete(coro)
        return r

    loop = asyncio.new_event_loop()
    threading.Thread(
        target=run_coro,
        args=(loop, coro)
    ).start()

def run_coroutine_in_current_thread(coro):
    loop = get_event_loop()
    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop)
    else:
        return loop.run_until_complete(coro)

def start_loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def new_loop_thread():
    loop = asyncio.new_event_loop()
    t = Thread(
        target=start_loop_in_thread,
        args=(loop,)
    )
    t.start()
    return loop, t

def is_picture_file(file_path):
    if PATTERN_PICTURE.match(file_path):
        return True
    else:
        return False

if __name__ == '__main__':
    import task_classes
    r = get_class_functions([task_classes, ])
    print(r)