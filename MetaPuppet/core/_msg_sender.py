# -*- coding: utf-8 -*-
import json
import threading
import time

import json
import pandas as pd
import collections
import os
import numpy as np
from SocketServer import SocketServer

def get_msg(nickName=None, mode=None):
    msg = None
    if mode == 'general':
        # general
        if nickName and nickName != 'None':
            msg = '新年快乐！祝' + nickName + '在新的一年里有“鼠”不尽的收获和幸福~'
        else:
            msg = '新年快乐！祝你在新的一年里有“鼠”不尽的收获和幸福~'
    elif mode == 'friend':
        # friend
        if nickName and nickName != 'None':
            msg = '新年快乐！祝' + nickName + '在新的一年里有“鼠”不尽的收获和幸福~'
        else:
            msg = '新年快乐！祝你在新的一年里有“鼠”不尽的收获和幸福~'
    elif mode == 'senior':
        # senior
        if nickName and nickName != 'None':
            msg = '新年快乐！祝' + nickName + '在新的一年里有“鼠”不尽的收获和幸福，身体健康，阖家欢乐~'
        else:
            msg = '新年快乐！祝您在新的一年里有“鼠”不尽的收获和幸福，身体健康，阖家欢乐~'
    else:
        msg = None

    return msg


def get_receiver_msg(msg_type):
    # goal
    all_msg = []

    # get data
    contacts = pd.read_excel('../generated/contacts_20200125_detail.xlsx')
    print('contacts.shape', contacts.shape)
    print(contacts.head())
    contacts['昵称'] = contacts['昵称'].apply(
        lambda x: 'None' if isinstance(x, float) and np.isnan(x) else x
    )
    sent_path = '../generated/sent_20200125.json'
    if os.path.exists(sent_path):
        with open(sent_path, 'r', encoding='utf-8') as fr:
            sent = json.load(fr)
    else:
        sent = []
    sent = set(map(
        lambda x: (x['alias'], x['name']),
        sent
    ))
    not_sent = contacts.apply(
        lambda x: (x['alias'], x['name']) not in sent,
        axis=1
    )
    contacts = contacts[not_sent]
    print('len(contacts) not_sent', len(contacts))

    # verify data, sum should be 1
    if len(contacts[contacts['sum'] != 1]) > 0:
        raise ValueError('sum is not 1')

    if msg_type in {'friend', 'senior', }:
        contacts_to_send = contacts[
            (contacts['单发'] == 1) &
            (contacts['不用发'] == 0) &
            (contacts['已发'] == 0) &
            (contacts['同时区'] == 1)
            ]
        if msg_type == 'senior':
            contacts_to_send = contacts_to_send[
                (contacts_to_send['老师'] == 1) |
                (contacts_to_send['长辈'] == 1)
                ]
        else:
            contacts_to_send = contacts_to_send[
                (~((contacts_to_send['老师'] == 1) |
                  (contacts_to_send['长辈'] == 1))) &
                ((contacts_to_send['好朋友']
                  +contacts_to_send['比较熟']
                  +contacts_to_send['一般熟']
                  +contacts_to_send['仅认识 需要发']
                  )>0)
            ]

    elif msg_type == 'general':
        contacts_to_send = contacts[
            (contacts['群发'] == 1) &
            (contacts['不用发'] == 0) &
            (contacts['已发'] == 0) &
            (contacts['同时区'] == 0)
            ]
    else:
        raise ValueError('msg_type {} is unknown'.format(msg_type))

    for tmp_row in contacts_to_send.itertuples(index=False):
        tmp_msg = {
            'alias': tmp_row.alias,
            'name': tmp_row.name,
            'msg': get_msg(nickName=tmp_row.昵称, mode=msg_type)
        }
        all_msg.append(tmp_msg)
    return all_msg



# We kick off our server
if __name__ == '__main__':
    from TestBot import TestBot

    # a_bot = TestBot(name='test')
    # a_server = SocketServer(
    #     robot=a_bot,
    #     debug_mode=True
    # )
    # # TODO: solve timeout problem
    # # https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs
    # threading.Timer(
    #     1,
    #     a_server.run,
    #     kwargs={
    #         'port': 8080
    #     },
    # ).start()
    # time.sleep(30)
    #
    # sent_path = '../generated/sent_20200125.json'
    # if os.path.exists(sent_path):
    #     with open(sent_path, 'r') as fr:
    #         sent = json.load(fr)
    # else:
    #     sent = []

    all_msg = []
    # all_msg.extend(get_receiver_msg(msg_type='senior'))
    all_msg.extend(get_receiver_msg(msg_type='friend'))
    # all_msg.extend(get_receiver_msg(msg_type='general'))
    # all_msg = all_msg[:5]
    print('len(all_msg)', len(all_msg))
    to_sent_path = '../generated/to_sent_20200125.json'
    with open(to_sent_path, 'w') as fw:
        json.dump(all_msg, fw, indent=2)

    for i, msg in enumerate(all_msg):
        if i%50==0:
            print('{}/{} msg done'.format(i, len(all_msg)))

        print(msg['name'])
        print(msg['msg'])
        print()
        # time.sleep(5)
        #
        # # get contact list
        # # r = a_server.exec_one_wx_function(
        # #     func_name='bot.Contact.findAll',
        # #     func_paras=[],
        # #     need_return=True,
        # # )
        # # print('r', r)
        # # with open('../generated/contacts_20200125.json', 'w') as fw:
        # #     json.dump(r, fw, indent=2)
        #
        # # if msg['alias'] is not None and msg['alias'] != '' and msg['alias'] != 'None':
        # #     a_server.exec_wx_function(
        # #         ts_code='''const a_person = await bot.Contact.find({{alias: '{}'}})
        # #         console.log(a_person)
        # #         await a_person.say('{}')
        # #         '''.format(msg['alias'], msg['msg']),
        # #         need_return=False,
        # #     )
        # # else:
        # a_server.exec_wx_function(
        #     ts_code='''try {{
        #     const a_person = await bot.Contact.find({{name: '{}'}})
        #     console.log(a_person)
        #     await a_person.say('{}')
        #
        # }} catch(err) {{
        # }}
        # '''.format(msg['name'], msg['msg']),
        #     need_return=False,
        # )
        # time.sleep(5)
        # sent.append(msg)
        # with open(sent_path, 'w') as fw:
        #     json.dump(sent, fw, indent=2)