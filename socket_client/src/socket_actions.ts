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
    await socket.emit("message", msg_to_send)
}

async function process_msg_from_server(msg: any) {
    console.log('process_msg_from_server ' + typeof msg)
    if ('type' in msg && msg['type'] === 'CMD_INFO') {
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
