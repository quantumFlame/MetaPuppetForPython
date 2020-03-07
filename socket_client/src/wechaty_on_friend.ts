import {Friendship } from "wechaty";

export async function on_friendship(request: any) {
    try {
        const contact = request.contact()

        if (request.type() === Friendship.Type.Confirm) {
            console.log('New friend ' + contact.name() + ' relationship confirmed!')
            return
        }

        if (request.type() === Friendship.Type.Receive) {
            const payload = await request.toJSON()
            console.log(payload)
            await request.accept()
            return
        }
    } catch (e) {
        console.log(e)
    }
}
