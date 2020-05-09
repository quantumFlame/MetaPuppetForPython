// with ES6 import
import * as io from 'socket.io-client'
import { Wechaty,       } from 'wechaty'
import * as config from '../config.json'

export const socket = io.connect(
    `http://${config.server.host}:${config.server.port}`
)
const token = config.token.windows
const name  = 'bot-windows'
export const bot = new Wechaty({
  puppet: 'wechaty-puppet-hostie',
  puppetOptions: {
    token,
  }
})



