// with ES6 import
import * as ts from 'typescript'
import { FileBox }  from 'file-box'

import {socket} from "./communication_agents";
import {wxbot} from "./communication_agents";
import {delay} from './utils'

const bot = wxbot

export async function send_msg_to_server(msg: any) {
    let msg_to_send: any = {
        'sender': 'wx_padplus',
        'status': 'NORMAL',
    }
    if (typeof msg === 'string') {
        msg_to_send['text'] = msg
    }
    else if (typeof msg === 'object') {
        msg_to_send = {...msg_to_send, ...msg}
    }
    else {
        msg_to_send['status'] = 'ERROR'
    }
    if ('type' in msg_to_send && msg_to_send['type'] === 'CMD_INFO') {
        console.log('send_msg_to_server: CMD_INFO')
        // console.log(msg_to_send)
    }
    // TODO: do we need await here?
    await socket.emit("message", msg_to_send)
}

async function process_msg_from_server(msg: any) {
    console.log('process_msg_from_server ' + typeof msg)
    if ('type' in msg &&
        msg['type'] === 'CMD_INFO'
    ) {
        //     https://stackoverflow.com/questions/45153848/evaluate-typescript-from-string
        let ts_code = ts.transpile(msg['ts_code'])
        let future_obj :any = eval(ts_code)
        let result = await future_obj
        if ('need_return' in msg &&
            msg['need_return'] === true &&
            'task_id' in msg) {
            const return_msg = {
                'type': 'CMD_INFO',
                'task_id': msg['task_id'],
                'cmd_return': result || null,
            }
            await send_msg_to_server(return_msg)
        }
    }
    else if ('type' in msg &&
        msg['type'] == 'CHAT_INFO'
    ) {
        let say_content:any = undefined
        if (msg['wx_msg_type'] == 'TEXT') {
            say_content = msg['text']
        }
        else if (msg['wx_msg_type'] == 'FILE') {
            say_content = FileBox.fromFile(msg['path'])
        }
        else if (msg['wx_msg_type'] == 'URLLINK') {
            say_content =  new bot.UrlLink({
                description: msg['description'],
                thumbnailUrl: msg['thumbnailUrl'],
                title : msg['title'],
                url : msg['url'],
            })
        }
        if (say_content) {
            let recover_msg_success = true
            // currently send back to message sender by defauly
            // maybe enable to send to anybody in the future
            // (combine send_text() with this function)
            // TODO: should be changed. use python and cmd to call rather than ts
            try {
                const ori_msg = bot.Message.load(msg['ori_msg']['id'])
                await ori_msg.ready()
                await ori_msg.say(say_content)
            } catch (e) {
                recover_msg_success = false
            }
            if (recover_msg_success === false) {
                if ('roomId' in msg['ori_msg']['payload'] &&
                    msg['ori_msg']['payload']['roomId']
                ) {
                    try {
                        const ori_room = bot.Room.load(msg['ori_msg']['payload']['roomId'])
                        await ori_room.ready()
                        await ori_room.say(say_content)
                    } catch (e) {}
                }
                else if ('fromId' in msg['ori_msg']['payload'] &&
                    msg['ori_msg']['payload']['fromId']
                ) {
                    try {
                        const ori_contact = bot.Contact.load(msg['ori_msg']['payload']['fromId'])
                        await ori_contact.ready()
                        await ori_contact.say(say_content)
                    } catch (e) {}
                }
            }
        }
    }
}

socket.on("connect", async function() {
    console.log('CONNECTED')
    await delay(5000)
    const msg = {
        'type': 'SOCKET_INFO',
        'text': 'CONNECTED',
    }
    await send_msg_to_server(msg)
})

socket.on("disconnect", function(reason: any) {
    console.log('DISCONNECTED')
})

socket.on("message", async function(msg: any) {
    await process_msg_from_server(msg)
})
