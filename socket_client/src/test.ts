let msg_to_send : any= {
    'sender': 'wx_padplus'
}

let msg_to_send2 : any = {
    'sender': 'qq',
    'status': 'new',
}

msg_to_send['msg'] = 'some thing'


msg_to_send['msg'] = 'some thing 242'

msg_to_send.msg2 = 'hello'

// msg_to_send = {...msg_to_send, ...msg_to_send2}
msg_to_send = {...msg_to_send2, ...msg_to_send}

let a : any = 10

console.log(msg_to_send)
console.log(typeof msg_to_send)

console.log(typeof a)

