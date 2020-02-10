// with ES6 import
import * as io from 'socket.io-client'
import * as ts from 'typescript'
import { Wechaty,       } from 'wechaty'
import { PuppetPadplus } from 'wechaty-puppet-padplus'
import { FileBox }  from 'file-box'
import QrcodeTerminal from 'qrcode-terminal'
import * as config from '../config.json'

const socket = io.connect(`http://${config.server.host}:${config.server.port}`)
const token = config.token.padplus
const puppet = 'wechaty-puppet-padplus'
const name  = 'bot-padplus'
const bot = new Wechaty({
  name,
  puppet,
  puppetOptions: { token }, // generate xxxx.memory-card.json and save login data for the next login
})

function delay(ms: number) {
    return new Promise( resolve => setTimeout(resolve, ms) );
}

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
    send_msg_to_server(msg)
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
            send_msg_to_server(return_msg)
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
        if (say_content) {
            let recover_msg_success = true
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
  .on('scan', (qrcode: any, status: any) => {
    QrcodeTerminal.generate(qrcode, {
      small: true
    })
  })
  .on('message', (msg: any) => {
    process_wx_message(msg)
  })
  .start()


