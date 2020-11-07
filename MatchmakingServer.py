import random
import socket
import time

#from _thread import all(*)
from _thread import *
import threading


from datetime import datetime
import json

#for requesting user info from AWSLamda
import requests

#For data synchoronize
clients_lock = threading.Lock()
connected = 0

listOfUser = {}
#waiting list for user, 
waitingList = [{"WaitingTime" : 0, "userList" : []}, #idx 0 for skill level 0 ~ 200
               {"WaitingTime" : 0, "userList" : []}, #idx 1 for skill level 201 ~ 400
               {"WaitingTime" : 0, "userList" : []}, #idx 2 for skill level 401 ~ 600
               {"WaitingTime" : 0, "userList" : []}, #idx 3 for skill level 601 ~ 800
               {"WaitingTime" : 0, "userList" : []}] #idx 4 for skill level 801 ~ 1000

simulationScriptAddr = ()

def AddToWaitingLobby(user_id) :
    #get user's skill level
    userSkillLevel = int(listOfUser[user_id]["skill_level"])

    #lock data
    clients_lock.acquire()

    #put user into proper waitingList
    if(userSkillLevel >= 801):
        waitingList[4]["userList"].append(user_id)
    elif(userSkillLevel >= 601):
        waitingList[3]["userList"].append(user_id)
    elif(userSkillLevel >= 401):
        waitingList[2]["userList"].append(user_id)
    elif(userSkillLevel >= 201):
        waitingList[1]["userList"].append(user_id)
    else:
        waitingList[0]["userList"].append(user_id)

    #release data
    clients_lock.release()

def RequestUserInfoFromAWSLamda(user_id) :
    #dictionary(key, value)
    queryParams = {"user_id" : user_id}
    
    #Request user info from AWSLamda, it gives JSON data
    resp = requests.get("https://a4g6194i43.execute-api.us-east-2.amazonaws.com/default/GetPlayerInfo", queryParams)

    #JSON data -> Dictionary(Python Object)
    respBody = json.loads(resp.content)

    return respBody

def connectionLoop(sock):
    global simulationScriptAddr

    while True:
        print("Start connectionLoop")

        #receive packet with size of 1024Bytes
        #and save packet in data, addr
        #[bits, [IP, PORT]] -> tuple, IP : sender of IP, PORT : sender of PORT
        data, addr = sock.recvfrom(1024)
        
        #if we don't have simulation script's address(IP, PORT)
        if simulationScriptAddr == () :
            #lock data
            clients_lock.acquire()

            simulationScriptAddr = addr

            #release data
            clients_lock.release()

        print("Got msg from client: ", addr[0], addr[1])

        #convert json data to python object
        convertedData = json.loads(data)

        #if data was connect msg, add new client to client list
        if convertedData["cmd"] == "Connect" :
            print("New client connected, get info of this player from AWSLamda")
            respBody = RequestUserInfoFromAWSLamda(convertedData["user_id"])
            
            #add new user to list of users
            listOfUser[respBody["user_id"]] = {}
            listOfUser[respBody["user_id"]]["user_id"] = respBody["user_id"]
            listOfUser[respBody["user_id"]]["name"] = respBody["name"]
            listOfUser[respBody["user_id"]]["skill_level"] = respBody["skill_level"]
            
            #add new user to waiting lobby
            AddToWaitingLobby(respBody["user_id"])
            print(respBody["user_id"] + " is added to waiting lobby")
            
            #send connection success msg
            connectedMsg = {"cmd" : "ConnectionSuccess", "user_id" : respBody["user_id"]}
            jsonConnectedMsg = json.dumps(connectedMsg)
            sock.sendto(bytes(jsonConnectedMsg,'utf8'), (addr[0], addr[1]))
          

#Waiting lobby for waiting players, periodically check waiting list and match the game or expand matching range
def WaitingLobby(sock) :
    global simulationScriptAddr
    #init game id
    gameID = 0

    while True:
        for i in range(5) :
            print("WaitingList" + str(i) + ": ", end='')
            for j in range(len(waitingList[i]["userList"])) :
                print(waitingList[i]["userList"][j] + " ", end='')
            print("")


        for i in range(5) :
            #if there is user in waiting list
            if len(waitingList[i]["userList"]) > 0 :
                #increase waiting time for list
                waitingList[i]["WaitingTime"] += 1

            #if there are more than 3 user in waiting list
            if len(waitingList[i]["userList"]) >= 3 :
                print("Match Found")
                
                #lock data
                clients_lock.acquire()

                #Get matched users
                matchedUsers = []
                for j in range(3) :
                    if waitingList[i]["userList"][j] in listOfUser :
                        matchedUsers.append(listOfUser[waitingList[i]["userList"][j]])

                #delete matched user from listOfUser
                for j in range(3) :
                    del listOfUser[waitingList[i]["userList"][j]]

                #delete matched user from waitingList
                for j in range(3) :
                    waitingList[i]["userList"].pop(0)               
                
                #reset waiting time of waiting list
                waitingList[i]["WaitingTime"] = 0

                #release data
                clients_lock.release()


                #send match found msg
                matchFoundMsg = {"cmd" : "MatchFound", 
                                 "users" : matchedUsers,
                                 "gameID" : gameID
                                }

                jsonMatchFoundMsg = json.dumps(matchFoundMsg)
                sock.sendto(bytes(jsonMatchFoundMsg,'utf8'), (simulationScriptAddr[0], simulationScriptAddr[1]))

                gameID += 1

        time.sleep(1)

def main():
   port = 12345

   #Create socket, type of UDP
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

   #bind new  socket to Local IP and port
   s.bind(('', port))

   #start thread
   #give funtion name and argument
   #start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(WaitingLobby,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()




############################SOLUTION#############################
"""

"""
#Import multiple modules that will be used in this script
"""
import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

########################
#GLOBALS
########################
# creating a lock for shared threads https://realpython.com/intro-to-python-threading/#working-with-many-threads
clients_lock = threading.Lock()
# num of connected clients
connected = 0
# a dictionary that will store our clients indexed by their (IP, PORT)
clients = {}

########################
#METHODS
########################


def connectionLoop(sock):
    
    #Takes care of:
    #  1. Updating the heartbeat of an existing client
    #  2. Connecting a new client 
    
    while True:
        # Listen to the next message
        data, addr = sock.recvfrom(1024)
        data = str(data)
        print("Got this: " + data)
        # if addr (i.e IP,PORT) exists in clients dictionary
        if addr in clients:
            # update the heartbeat value if data dictionary has a key called 'heartbeat'
            if 'heartbeat' in data:
                clients[addr]['lastBeat'] = datetime.now()
        else:
            # if there is a key called 'connect' in data dictionary
            if 'connect' in data:
                # add a new object to the client dictionary
                clients[addr] = {}
                # update the last beat of the client object
                clients[addr]['lastBeat'] = datetime.now()
                # add a field called color
                clients[addr]['color'] = 0
                # create a message object with a command value and an array of player objects
                message = {"cmd": 0, "players": []}  # {"id":addr}}

                # create a new object
                p = {}
                # add a field called 'id' that is the string version of (IP, PORT)
                p['id'] = str(addr)
                # create a field called color
                p['color'] = 0
                # add the object to the player array
                message['players'].append(p)

                # create a new gamestate object similar to message
                GameState = {"cmd": 4, "players": []}
                # for every key of clients
                for c in clients:
                    # if the key is the same as the connected player
                    if (c == addr):
                        # change command to 3
                        message['cmd'] = 3
                    else:
                        message['cmd'] = 0

                    # create a JSON string.
                    # google what the separator function does. Why do we use it here? Its not always needed.
                    m = json.dumps(message, separators=(",", ":"))

                    # create a new player object
                    player = {}
                    # set the id to the current key
                    player['id'] = str(c)
                    # set the color to the key's properties
                    player['color'] = clients[c]['color']
                    # add it to the game state
                    GameState['players'].append(player)
                    # send the message object containg the new connected client to the previously connected clients
                    sock.sendto(bytes(m, 'utf8'), (c[0], c[1]))

                # send the game state to the new client
                m = json.dumps(GameState)
                sock.sendto(bytes(m, 'utf8'), addr)


def cleanClients(sock):
    
      #Takes care of:
      #   1. Checking if a client should be dropped
      #   2. Letting the clients know of a drop
    
    while True:
        # create an array
        droppedClients = []
        # for every client in keys
        # How is this different from what we did in line 67? Try and find out.
        for c in list(clients.keys()):
            # Check if its been longer than 5 seconds since the last heartbeat
            if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
                print('Dropped Client: ', c)
                # for thread safety, gain the lock
                clients_lock.acquire()
                # delete the client identified by c
                del clients[c]
                # releast the lock we have
                clients_lock.release()
                # add the dropped client key to the array of dropped clients
                droppedClients.append(str(c))

        # Send a JSON object with list of dropped clients to all connected clients
        message = {"cmd": 2, "droppedPlayers": droppedClients}
        m = json.dumps(message, separators=(",", ":"))

        if (len(droppedClients) > 0):
            for c in clients:
                sock.sendto(bytes(m, 'utf8'), (c[0], c[1]))

        time.sleep(1)


def gameLoop(sock):
    
      #Takes care of:
      #   1. Assigning a random color to every client
      #   2. Send the state to all clients
    

    pktID = 0  # just to identify a particular network packet while debugging
    while True:
        print("Boop")
        # create a game state object
        GameState = {"cmd": 1, "pktID": pktID, "players": []}
        clients_lock.acquire()
        #      print (clients)
        for c in clients:
            # create a player object
            player = {}
            # assign a random color
            clients[c]['color'] = {
                "R": random.random(),
                "G": random.random(),
                "B": random.random()
            }
            # fill the player details
            player['id'] = str(c)
            player['color'] = clients[c]['color']
            GameState['players'].append(player)
        s = json.dumps(GameState, separators=(",", ":"))
        #      print(s)
        # send the gamestate json to all clients
        for c in clients:
            sock.sendto(bytes(s, 'utf8'), (c[0], c[1]))
        clients_lock.release()
        if (len(clients) > 0):
            pktID = pktID + 1
        time.sleep(1)


########################
# ENTRY 
########################


def main():
    print("Running server")
    
      #Start 3 new threads 
    
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    start_new_thread(gameLoop, (s, ))
    start_new_thread(connectionLoop, (s, ))
    start_new_thread(cleanClients, (s, ))
    # keep the main thread alive so the children threads stay alive
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()


"""