import * as fs from 'fs'


function delay(ms: number) {
    return new Promise( resolve => setTimeout(resolve, ms) );
}

async function sent_msg() {
    let msg_to_sent_buffer =fs.readFileSync('generated/to_sent_20200125.json')
    let msg_to_sent = JSON.parse(msg_to_sent_buffer.toString())
    let msg_sent_buffer =fs.readFileSync('generated/sent_20200125.json')
    let msg_sent = JSON.parse(msg_sent_buffer.toString())
    console.log('msg_sent.length ' + msg_sent.length)
    console.log('msg_to_sent.length ' + msg_to_sent.length)
    console.log('\n')
    for (let i = 0; i < 3; i++) {
        // console.log(msg)
        let msg = msg_to_sent.pop()

        // const a_person = await bot.Contact.find({{name: msg['name']}})
        // console.log(a_person)
        // await a_person.say(msg['msg']  )

        await delay(100);
        msg_sent.push(msg)
        console.log('msg_sent.length ' + msg_sent.length)
        console.log('msg_to_sent.length ' + msg_to_sent.length)

        if (msg_to_sent.length === 0) {
            break
        }
    }
    console.log('\nmsg_sent.length ' + msg_sent.length)

    fs.writeFile(
        'generated/sent_20200125.json',
        JSON.stringify(msg_sent),
        function(err) {
            if (err) {
                console.error(err)
                return
            }
            console.log("File has been created")
        }
    )
}

sent_msg()

