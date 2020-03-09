import {Friendship } from "wechaty";
import {send_msg_to_server} from './socket_actions'

export async function on_friendship(request: any) {
    try {
        if (request.type() === Friendship.Type.Confirm) {
            const contact = request.contact()
            console.log('New friend ' + contact.name() + ' relationship confirmed!')
            return
        }

        if (request.type() === Friendship.Type.Receive) {
            const payload = await request.toJSON()
            const msg = {
                'payload': payload,
                'type': 'FRIEND_INFO'
            }
            await send_msg_to_server(msg)
            return
        }
    } catch (e) {
        console.log(e)
    }
}
