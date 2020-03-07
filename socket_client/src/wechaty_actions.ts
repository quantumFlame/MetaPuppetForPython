// with ES6 import
import QrcodeTerminal from 'qrcode-terminal'

import {wxbot} from "./communication_agents";
import {on_message} from "./wechaty_on_message";
import {on_friendship} from "./wechaty_on_friend";
import {on_room_invite} from "./wechaty_on_room";

const bot = wxbot

bot
.on('scan', (qrcode: any, status: any) => {
    QrcodeTerminal.generate(qrcode, {
        small: true
    })
})

.on('login', async function (this, user) {
    console.log('Bot', `${user.name()} logined`)
})
.on('logout', user => console.log('Bot', `${user.name()} logouted`))

.on('error', error => console.log('Bot', 'error: %s', error))

.on('message', on_message)
.on('friendship', on_friendship)
.on('room-invite',  on_room_invite)

.start()


