# MetaPuppetForPython

Utilize socket to communicate between python and ts. 
MetaPuppetForPython is capable of calling native ts functions from `Wechaty`.

Install:  

	git clone https://github.com/quantumFlame/MetaPuppetForPython.git
	cd MetaPuppetForPython
    pip install .

    cd socket_client
    # install node.js
    # https://github.com/nodesource/distributions/blob/master/README.md
    # Using Ubuntu
    curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
    sudo apt-get install -y nodejs
    npm install -g ts-node
    npm install -g typescript  
    sudo apt-get install autoconf
    sudo apt-get install libtool

    npm install 
    # or    
    # rm -rf node_modules package-lock.json 
    # npm install wechaty@latest
    # npm install wechaty-puppet-padplus@next
    # npm install qrcode-terminal
    # npm install socket.io-client
    # npm install @types/socket.io-client
    # npm install @types/node
    
    # (before you run, you need a wechaty token and 
    # create the config.json file following 
    # the example config.example.json)
    ts-node src/client_wechaty.ts

Use:

	see example/hello_world.py

Keys to remember:
* Extend `RobotBase` and modify `_process_message()` to reply to various wechat messages.

* Compile your management tasks as `async_foo()` and call with `run_coroutine_in_new_thread()`. 
****************
* If you don't like async, you can also run the sync version functions in new thread (see more details in `hello_world.py`).
