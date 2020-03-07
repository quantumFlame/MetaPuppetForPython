export async function on_room_invite(roomInvitation: any) {
    try {
        console.log(`received room-invite event.`)
        await roomInvitation.accept()
    } catch (e) {
        console.error(e)
    }
}


