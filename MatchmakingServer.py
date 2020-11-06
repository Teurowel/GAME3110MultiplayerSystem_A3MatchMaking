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
          
          #check if we have more than 3 players
        #   if(len(listOfUser) >= 3):
        #       print("Fidning match..")
        #       matchFoundMsg = {"cmd" : "MatchFoundResult", "Result" : "Yes"}
        #       jsonMatchFoundMsg = json.dumps(matchFoundMsg)
        #       sock.sendto(bytes(jsonMatchFoundMsg,'utf8'), (addr[0], addr[1]))
        #   #if we don't have enough player to make match, send msg that we couldn't make match
        #   else :
        #       print("Need more players")
        #       matchFoundMsg = {"cmd" : "MatchFoundResult", "Result" : "No"}
        #       jsonMatchFoundMsg = json.dumps(matchFoundMsg)
        #       sock.sendto(bytes(jsonMatchFoundMsg,'utf8'), (addr[0], addr[1]))




      #check if addr(key) is in clients(dictionary)
#       if addr in clients:
#          #check if 'heartbeat' object(property) is in data
#          #heartheat is used to check wheter client is still connected, client will sned hearthaed every second
#          if 'heartbeat' in data:
#             clients[addr]['lastBeat'] = datetime.now()
#             #print("heatbeat")
         
#          #Extract position value(x, y, z)
#          elif "position" in data:
#             pos = []
#             for num in data.split():
#                if IsFloat(num):
#                   pos.append(float(num))

#             clients[addr]["pos"]["X"] = pos[0]
#             clients[addr]["pos"]["Y"] = pos[1]
#             clients[addr]["pos"]["Z"] = pos[2]

#          #Extract rotation value(x, y, z)
#          elif "rotation" in data:
#             rot = []
#             for num in data.split():
#                if IsFloat(num):
#                   rot.append(float(num))

#             clients[addr]["rot"]["X"] = rot[0]
#             clients[addr]["rot"]["Y"] = rot[1]
#             clients[addr]["rot"]["Z"] = rot[2]

#       #if it was new client
#       else:
#          if 'connect' in data:
#             ####################Send IP and PORT info to sender######################
#             #SENDER_IP_PORT
#             senderIPPORT = {"cmd" : 4,
#                             "IP" : addr[0],
#                             "PORT" : addr[1]}

#             sIP = json.dumps(senderIPPORT)

#             sock.sendto(bytes(sIP,'utf8'), (addr[0], addr[1]))
#             ###############################################################


#             ####################Send all client info to new client######################
#             #2 = ALL_CLIENT_INFO
#             AllClientInfo = {"cmd": 2, "players": []}

#             for c in clients:
#                player = {}
#                player['id'] = str(c)
#                player['color'] = clients[c]['color']
#                player["pos"] = clients[c]["pos"]
#                player["rot"] = clients[c]["rot"]
#                AllClientInfo['players'].append(player)

#             aci = json.dumps(AllClientInfo)

#             #send all clients info to new client
#             sock.sendto(bytes(aci,'utf8'), (addr[0], addr[1]))

#             # allClientsInfo = {"cmd" : 2,
#             #                   "numOfClients" : len(clients),
#             #                   "allClients" : []}

#             # for c in clients:
#             #    clientInfo = {}
#             #    clientInfo["IP"] = c[0]
#             #    clientInfo["PORT"] = c[1]
#             #    allClientsInfo["allClients"].append(clientInfo)

#             # aci = json.dumps(allClientsInfo)
#             # #send all clients info to new client
#             # sock.sendto(bytes(aci,'utf8'), (addr[0], addr[1]))
#             ###############################################################


#             ################Send new client info to all existed client###################
#             #make message
#             # message = {"cmd" : 0,
#             #            "newClient" : {"id" : str(addr)}
#             #           }

#             newClientInfo = {"cmd" : 0,
#                        "id" : str(addr),
#                        "color" : {"R" : 1, "G" : 1, "B" : 1},
#                        "pos" : {"X" : 0, "Y" : 0, "Z" : 0},
#                        "rot" : {"X" : 0, "Y" : 0, "Z" : 0}
#                       }

#             #convert python object(message) into json string
#             nci = json.dumps(newClientInfo) 
 
#             #loop through all clinets(distionary) and get addr(key)
#             #and using addr(key) send message
#             for c in clients:
#                #send m to c[0](IP), c[1](PORT)
#                sock.sendto(bytes(nci,'utf8'), (c[0],c[1]))
#             ################################################################



#             #####################Add new client to list####################
#             #make new pair
#             clients[addr] = {}
#             #populate info
#             clients[addr]['lastBeat'] = datetime.now()
#             clients[addr]['color'] = {"R" : 1, "G" : 1, "B" : 1}
#             clients[addr]["pos"] = {"X" : 0, "Y" : 0, "Z" : 0}
#             clients[addr]["rot"] = {"X" : 0, "Y" : 0, "Z" : 0}
#             ################################################################

            
          


           


#             ###################print all client ##########################
#             idx = 0
#             for player in clients:
#                print("Player " + str(idx))
#                print("IP: " + player[0])
#                print("PORT: " + str(player[1]))
#                idx += 1
#                print("")
#             ###############################################################
# def gameLoop(sock):
#    lastTimeUpdatedColor = datetime.now()
#    ShouldChangeColor = False
#    while True:
#       print("game loop")
      
#       GameState = {"cmd": 1, "players": []}

#       #every 1second, update player's color
#       if (datetime.now() - lastTimeUpdatedColor).total_seconds() > 1:
#          ShouldChangeColor = True

#       #block
#       clients_lock.acquire()
#       #print (clients)
#       for c in clients:
#          player = {}
         
#          #every 1second, update player's color
#          if (ShouldChangeColor == True):
#             clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}

#          player['id'] = str(c)
#          player['color'] = clients[c]['color']
#          player["pos"] = clients[c]["pos"]
#          player["rot"] = clients[c]["rot"]
#          #notify updated pos to all other clients 


#          GameState['players'].append(player)
#       s=json.dumps(GameState)
#       #print(s)
#       for c in clients:
#          sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      
#       #relase the lock
#       clients_lock.release()


#       if(ShouldChangeColor == True):
#          ShouldChangeColor = False
#          lastTimeUpdatedColor = datetime.now()




#       time.sleep(0.01)

# def cleanClients(sock):
#    while True:
#       print("clean loop")
#       #loop all clinets
#       for c in list(clients.keys()):
#          #check time if lastbeat(client update this every second) has gone over 5second
#          if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
#             print('Dropped Client: ', c)

#              #3 for DISCONNECTED_CLIENT
#             disconnectedClientID = {"cmd" : 3,
#                                     "id" : str(c)}

#             dci = json.dumps(disconnectedClientID)

#             #Send message to all client that this client is disconnected
#             for player in clients:
#                #if it is the disconnected player, skip
#                if(player == c):
#                   continue
               
#                #send disconnected clients info to all client
#                sock.sendto(bytes(dci,'utf8'), (player[0], player[1]))

#             #lock data
#             clients_lock.acquire()

#             del clients[c]

#             #release data
#             clients_lock.release()
#       time.sleep(1)

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