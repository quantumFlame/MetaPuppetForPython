// with ES6 import
import * as io from 'socket.io-client'
import { Wechaty,       } from 'wechaty'
import { PuppetPadplus } from 'wechaty-puppet-padplus'
import * as config from '../config.json'

export const socket = io.connect(
    `http://${config.server.host}:${config.server.port}`
)
const token = config.token.padplus
const puppet = 'wechaty-puppet-padplus'
const name  = 'bot-padplus'
export const bot = new Wechaty({
  name,
  puppet,
  puppetOptions: { token }, // generate xxxx.memory-card.json and save login data for the next login
})

