# Chat server
- Pythno + Django + rest-framework based chatting service

## Pre-requisites (How to deploy)
- Install Python 3.X
    ```
    sudo add-apt-repository ppa:jonathonf/python-3.6
    sudo apt-get update
    sudo apt-get install python3.6
    sudo apt install python3-pip
    ```
    - If you have multiple versions of python in your system, set 3.X as default one
        ```
        alias python=python3
        ```
- Install & execute RabbitMQ on your system 
    - How to install : Do refer the guide from the official site (https://www.rabbitmq.com/download.html)
- Install packages enlisted in `requirements.txt`
    ```
    pip3 install -r requirements.txt
    ```
- Install curl for testing the APIs
    ```
    sudo apt install curl
    ```
- Intialize chat-backend server
    ```
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```
    
## How to run (chat service)
- Execute RabbitMQ server (administrator mode) 
    ```
    service rabbitmq-server start
    ```
- Execute Celery (which plays role as a message broker between backend web API server & msg deliver server)
    ```
    celery -A chat_backend worker -l info
    ```
- Execute chat-backend API server instance
    ```
    python3 manage.py runserver
    ```
- Execute chat-backend message deliver server instance
    ```
    uwsgi --http :8081 --module msg_deliver --master --processes 4
    ```
    
## How to start chatting
- Sign up to chat server
    1. user a
    ```
    request : curl -X POST http://127.0.0.1:8000/auth/users/create/ --data 'username=user_a&password=1234qwer&email=user_a@mail.com'
    response :{"email":"user_a@mail.com","username":"user_a","id":1}
    ```
    2. user b
    ```
    request : curl -X POST http://127.0.0.1:8000/auth/users/create/ --data 'username=user_b&password=1234qwer&email=user_b@mail.com'
    response :{"email":"user_b@mail.com","username":"user_b","id":2}
    ```
- Sing in to get a auth_token for creating/joining a chat room (Chat room creator)
    1. user a
    ```
    request : curl -X POST http://127.0.0.1:8000/auth/token/login/ --data 'username=user_a&password=1234qwer'
    response : {"auth_token":"0e067205dbfe798b8a7e35b2b7599a95d336a000"}    
    ``` 
    2. user b
    ```
    request : curl -X POST http://127.0.0.1:8000/auth/token/login/ --data 'username=user_b&password=1234qwer'
    response : {"auth_token":"d167d69e1120e70b90a8819c08eadd082b8d649b"}    
    ``` 
- Get a chat room(session) for chatting (by user_a)
    ```
    request : curl -X POST http://127.0.0.1:8000/api/chats/ -H 'Authorization: Token 0e067205dbfe798b8a7e35b2b7599a95d336a000'
    response : {"status":"SUCCESS","uri":"040213b14a02451","message":"New chat session created"}
    ```
- Join a chat room(session) for chatting (by user_b)
    - Chat room (session : '040213b14a02451') uri should be shared to target user, user_b (ex : http://127.0.0.1:8000/api/chats/040213b14a02451/)
    ```
    request : curl -X PATCH http://127.0.0.1:8000/api/chats/040213b14a02451/ --data 'username=user_b' -H 'Authorization: Token d167d69e1120e70b90a8819c08eadd082b8d649b'
    response : {
                   "status":"SUCCESS","members":[
                       {"id":1,"username":"user_a","email":"user_a@mail.com","first_name":"","last_name":""},
                       {"id":2,"username":"user_b","email":"user_b@mail.com","first_name":"","last_name":""}
                   ],
                   "message":"user_b joined that chat","user":{
                       "id":2,"username":"user_b","email":"user_b@mail.com","first_name":"","last_name":""
                   }
               }
    ```
- Post a new message into the chat room(session)
    * Before start chatting, all the members of the chatting room (session) should made a Websocket connection 
      to msg_deliver server(ws://localhost:8081/{session_uri}, ex: session_uri=040213b14a02451)
        - Assuming each & all the members has made such connections, here's how to simulate receiving message 
        ```
        cd chat_client
        python3 msg_receiver.py -u 040213b14a02451
        ```

    1. user a
    ```
    request : curl -X POST http://127.0.0.1:8000/api/chats/040213b14a02451/messages/ --data 'message=Hello!' -H 'Authorization: Token 0e067205dbfe798b8a7e35b2b7599a95d336a000'
    response : {
                  "status":"SUCCESS",
                  "uri":"040213b14a02451",
                  "message":"Hello!",
                  "user":{"id":1,"username":"user_a","email":"user_a@mail.com","first_name":"","last_name":""}
               }
    msg_receiver : 125 {
                        "user": {
                            "id": 1,
                            "username": "user_a",
                            "email": "user_a@mail.com",
                            "first_name": "",
                            "last_name": ""
                        },
                        "message": "Hello!"
                    }
    ```
    2. user b
    ```
    request : curl -X POST http://127.0.0.1:8000/api/chats/040213b14a02451/messages/ --data 'message=Hi!' -H 'Authorization: Token d167d69e1120e70b90a8819c08eadd082b8d649b'
    response : {
                  "status":"SUCCESS",
                  "uri":"040213b14a02451",
                  "message":"Hi!",
                  "user":{"id":2,"username":"user_b","email":"user_b@mail.com","first_name":"","last_name":""}
               }
    msg_receiver : 135 {
                       "user": {
                           "id": 2,
                           "username": "user_b",
                           "email": "user_b@mail.com",
                           "first_name": "",
                           "last_name": ""
                       },
                       "message": "Hi!"
                   }
    ```
- Get all the chat rooms(sessions) that user created
    1. user a
    ```
    request : curl -X GET http://127.0.0.1:8000/api/chats/ -H 'Authorization: Token 0e067205dbfe798b8a7e35b2b7599a95d336a000'
    response : {
                   "status":"SUCCESS",
                   "sessions":[
                       {
                           "uri":"040213b14a02451",
                           "members":[
                               {"id":1,"username":"user_a","email":"user_a@mail.com","first_name":"","last_name":""},
                               {"id":2,"username":"user_b","email":"user_b@mail.com","first_name":"","last_name":""}
                           ]
                       }
                   ]
                }
    ```
- Get all the messages sent on the chat room(session)
    1. user a
    ```
    request : curl -X GET http://127.0.0.1:8000/api/chats/040213b14a02451/messages/ -H 'Authorization: Token 0e067205dbfe798b8a7e35b2b7599a95d336a000'
    response : {
                    "id":4,"uri":"040213b14a02451","messages":[
                        {"user":{"id":1,"username":"user_a","email":"user_a@mail.com","first_name":"","last_name":""},"message":"Hello!"},
                        {"user":{"id":2,"username":"user_b","email":"user_a@mail.com","first_name":"","last_name":""},"message":"Hi!"}
                    ]
                }
    ```

- Remove messages which has expired the given days from now
    - S/W Architectural point of view, the data management function should be separated from the API server in several aspects,
        1. It would influence the latency performance of the API server
        2. It would be difficult to maintain the all orthogonal functions in one codebase (Separation of Concerns)
    - There're 2 ways to have this "Data cleaning features" as follows
        1. (Assuming DB support trigger feature), Set scheduled trigger functions so that it could clean data by itself periodically
        2. Implement Scheduled service to clean the data periodically
    - Code reference (msg_cleaner.py). One can use "Celery" to schedule the cleaning task with msg_cleaner.py
        - Manual execution by the external scheduled service (Clean all the message which are older than 2 days..)
        ```
        python3 msg_cleaner.py -d 2
        ```
        - Scheduling cleaning task with 'Celery F/W'
        ```
        celery -A msg_cleaner worker -l info
        ```
      
## API List
1. User registration      : POST  http://{backend_api_ip}:8000/auth/user/create
2. User login             : POST  http://{backend_api_ip}:8000/auth/user/login
3. Chat session creation  : POST  http://{backend_api_ip}:8000/api/chats
4. Chat seesion list      : GET   http://{backend_api_ip}:8000/api/chats
5. Chat session join      : PATCH http://{backend_api_ip}:8000/api/chats/{session_uri}
6. Chat message send      : POST  http://{backend_api_ip}:8000/api/chats/{session_uri}/messages
7. Chat message read      : GET   http://{backend_api_ip}:8000/api/chats/{session_uri}/messages
8. Chat message receive   : WebSocketClient ws://{msg_deliver_server_ip}:8081/${session_uri}
* After the user registration, you could access the APIs doc link :`http://localhost:8000/docs/`
    - Registered user id & pw is required

## Reference
- How the message delivered in real-time to those users in a chat room
   1. When user x creates a chat room(session), he/she will receive chat session uri from the Backend server.
   ```
      -------- Create Chat Session -------> Backend API
     |                                           |
   User A <------------session_uri---------------                                       User B

                                           Backend WebSock
   ```
   2. And then he/she have to create channel with backends server with session_uri 
      to receives chat message shared in chat room.
    ```  
                                            Backend API
                                                
   User A                                                                                User B
     |
      ------ Websock (session_uri) ------> Backend WebSock
   ```
   3. And the user A should share the session uri to the target user (say B) to chat.
      Note : Logic for sharing session uri in the backend server side has not implemented. 
             This can be done on the frontend or client application by having default comm. channel 
             between backend ..
   ```
                                            Backend API
                                                
   User A  -------------------------------- session uri  ----------------------------->  User B
    
                                          Backend WebSock 
   ```                                           
   4. User B can join the chat room(session) thru Backend API, and also need to create (websock) channel 
   ```
                                            Backend API <-------- Join Chat Session ------- 
                                                                                          |
   User A                                                                                User B
                                                                                          |
                                           Backend WebSock  <--- WebSock (session_uri) ----
   ```
   
   5. User A or B can now chat (backend server will published the message to chat members thru websock channel)
   ```
     ------------ Message M-1 -----------> Backend API  
     |                                           |                                           
   User A                                        |                                       User B
     |                                          \/                                         |
     <------------ Message M-1 ----------- Backend WebSock  -------- Message M-1 ---------->
   ```  
   ```
                                           Backend API  <---------- Message M-2 ------------
                                                 |                                         |
   User A                                        |                                       User B
     |                                          \/                                         |
     <------------ Message M-2 ----------  Backend WebSock  -------- Message M-2 ---------->
   ``` 