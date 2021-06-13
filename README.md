# Messaging-System
A python django rest server that is responsible for handling messages between users.

* Server Link - https://messages-sys.herokuapp.com 

* Admin django back office - https://messages-sys.herokuapp.com/admin. \
username: admin\
password: herolo21

* Initially in order to test the server you need to get the JWT with the request 'Post user and get the JWT'\
(You can edit in 'body' -->  'from data' which user you want to get)\
Then copy the token and add it manually in the rest of the requests. 

* In addition, in the main folder of this repo there is a Postman file that you can import and send the requests to the server.

* To send a new message post request you can use this format in the body. \
{\
"reciever": "1",\
"subject": "String",\
"body": "String"\
}
