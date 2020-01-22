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
    console.log(msg)
    if ('type' in msg && msg['type'] === 'CMD_INFO') {
        console.log('some thing is here')
        console.log(msg['ts_code'])
//         {
//             const a_person  = await bot.Contact.find('会上网的机器人')
//             console.log(a_person)
//         }

        //     https://stackoverflow.com/questions/45153848/evaluate-typescript-from-string
        let ts_code = ts.transpile(msg['ts_code'])
        console.log(ts_code)
        let result :any = eval(ts_code)
        console.log(result)
        const r1 = await result
        console.log(r1)


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

socket.on("message", function(msg: string) {
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


