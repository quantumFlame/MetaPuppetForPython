# MetaPuppetForPython

Utilize socket to communicate between python and ts. 
MetaPuppetForPython is capable of calling native ts functions from `Wechaty`.

Install:  

	git clone https://github.com/quantumFlame/MetaPuppetForPython.git
	cd MetaPuppetForPython
    pip install .

    cd socket_client
    npm install 
    (before you run, you need a wechaty token and 
    update the create config.json file following 
    the example config.example.json)
    ts-node src/client_wechaty.ts

Use:

	see example/hello_world.py

Keys to remember:
* Extend `RobotBase` and `modify _process_message()` to reply to various wechat messages.

* Compile your management `tasks as async_foo()` and call with `run_coroutine_in_random_thread()`. 
Even better to use `new_loop_thread()` to create a new loop to avoid blocking. 
Refer to `SocketServer.create_app()` and `SocketServer.run_coroutine_in_random_thread()`.

