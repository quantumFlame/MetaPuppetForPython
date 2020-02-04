# -*- coding: utf-8 -*-
import asyncio
import inspect
from threading import Thread


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
        raise ValueError(
            'loop is running in get_event_loop(). '
            'By design, this function is only called by sync functions. '
            'Please make sure loop is not running, '
            'otherwise, call the async version instead or wrap the parent '
            'funtion which called this one in a new thread to avoid '
            'conflict with current loop '
        )
    return loop

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


if __name__ == '__main__':
    import task_classes
    r = get_class_functions([task_classes, ])
    print(r)