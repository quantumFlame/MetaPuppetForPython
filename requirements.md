## python

1. pip install python-socketio  
2. pip install sanic  
3. pip install regex

## node 
1. install dependencies

        cd socket_client   
        npm install   

2. (dev) enable real-time coding-compiling    

        npm install -g  nodemon
        cd socket_client
        edit nodemon.json to change the script to run if necessary
        nodemon    

3. (production) run client to pass messages to server

        cd socket_client
        ts-node src/wechaty_actions.ts
