import {send_msg_to_server} from './socket_actions'

async function process_wx_message(msg: any) {
    console.log('process_wx_message ' + typeof msg)
    // console.log(msg)
    msg['type'] = 'CHAT_INFO'
    await send_msg_to_server(msg)
}

export async function on_message(msg: any) {
    try
    {
        await process_wx_message(msg)
    } catch (e) {
        console.error(e)
    }
}
