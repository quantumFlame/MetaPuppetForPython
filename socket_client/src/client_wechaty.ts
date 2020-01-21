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
        'status': 'normal',
    }
    if (typeof msg === 'string') {
        msg_to_send['plain_message'] = msg
    }
    else if (typeof msg === 'object') {
        msg_to_send = {...msg_to_send, ...msg}
    }
    else {
        msg_to_send['status'] = 'error'
    }
    socket.emit("message", msg_to_send)
}

function process_wx_message(msg: any) {
    console.log('process_wx_message ' + typeof msg)
    console.log(msg)
    send_msg_to_server(msg)
}


function process_msg_from_server(msg: string) {
    console.log('process_msg_from_server ' + typeof msg)
    console.log(msg)
//     console.log('some thing is here')
//     console.log(data)
// //     https://stackoverflow.com/questions/45153848/evaluate-typescript-from-string
//     let result = ts.transpile(data)
//     let runnable :any = eval(result)
//     console.log(runnable)
//     console.log(result)
//     socket.emit("message", runnable)
    // socket.emit("message", "message received")
}

socket.on("connect", function() {
    socket.emit("message", "connected to server!")
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


