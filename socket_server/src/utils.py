# -*- coding: utf-8 -*-


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
