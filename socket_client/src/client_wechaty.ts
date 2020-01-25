// with ES6 import
import * as io from 'socket.io-client'
import * as ts from 'typescript'
import { Wechaty       } from 'wechaty'
import { PuppetPadplus } from 'wechaty-puppet-padplus'
import QrcodeTerminal from 'qrcode-terminal'
import * as config from '../config.json'

const token = config.token.padplus
const socket = io.connect(`http://${config.server.host}:${config.server.port}`)
const puppet = new PuppetPadplus({
    token,
})
const name  = 'bot-padplus'
const bot = new Wechaty({
    puppet,
    name, // generate xxxx.memory-card.json and save login data for the next login
})

function send_msg_to_server(msg: any) {
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
        console.log('msg_to_send')
        console.log(msg_to_send)
    }
    socket.emit("message", msg_to_send)
}

function process_wx_message(msg: any) {
    console.log('process_wx_message ' + typeof msg)
    // console.log(msg)
    msg['type'] = 'CHAT_INFO'
    // send_msg_to_server(msg)
}


async function process_msg_from_server(msg: any) {
    console.log('process_msg_from_server ' + typeof msg)
    console.log(msg)
    if ('type' in msg &&
        msg['type'] === 'CMD_INFO'
    ) {
        //     https://stackoverflow.com/questions/45153848/evaluate-typescript-from-string
        let ts_code = ts.transpile(msg['ts_code'])
        let future_obj :any = eval(ts_code)
        let result = await future_obj
        console.log(result)
        if ('need_return' in msg &&
            msg['need_return'] === true &&
            'task_id' in msg) {
            const return_msg = {
                'type': 'CMD_INFO',
                'task_id': msg['task_id'],
                'cmd_return': result || null,
            }
            send_msg_to_server(return_msg)
        }
    }
//     socket.emit("message", runnable)
    // socket.emit("message", "message received")
}

socket.on("connect", function() {
    const msg = {
        'type': 'SOCKET_INFO',
        'text': 'CONNECTED',
    }
    send_msg_to_server(msg)
})

socket.on("disconnect", function() {
    const msg = {
        'type': 'SOCKET_INFO',
        'text': 'DISCONNECTED',
    }
    send_msg_to_server(msg)
})

socket.on("message", function(msg: any) {
    process_msg_from_server(msg)
})

bot
  .on('scan', (qrcode, status) => {
    QrcodeTerminal.generate(qrcode, {
      small: true
    })
  })
  .on('message', msg => {
    process_wx_message(msg)
  })
  .start()


