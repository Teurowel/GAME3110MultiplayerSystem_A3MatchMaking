import random
import socket
import time

#from _thread import all(*)
from _thread import *
import threading


from datetime import datetime
import json

#For data synchoronize
clients_lock = threading.Lock()
connected = 0

clients = {}

serverIP = "127.0.0.1"
serverPort = 12345

def connectionLoop(sock):
   while True:
      #receive packet with size of 1024Bytes
      #and save packet in data, addr
      #[bits, [IP, PORT]] -> tuple, IP : sender of IP, PORT : sender of PORT
      print("Start connectionLoop")
      #try:
      data, addr = sock.recvfrom(1024)
      print("Client join request: " + addr)
      #except socket.error:
      #   print("Errlro")

      #print("connection loop")

      #send packet
      #can only send bytes datatype,  send "hello!" with 'utf8' format to addr[0](IP) and addr[1](PORT)
      #sock.sendto(bytes("Hello!",'utf8'), (addr[0], addr[1]))

      #convert data to string
      data = str(data)

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

def Client(sock) :
   #######################First send connecting msg, server will add this client as new client######################
   connectMsg = {"cmd" : "Connect"}
   jsonConnectMsg = json.dumps(connectMsg)
   sock.sendto(bytes(jsonConnectMsg,'utf8'), (serverIP, serverPort))
   ########################################################################

def main():
    #Create socket, type of UDP
    for x in range(5):
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      start_new_thread(Client, (sock, ))



   #  testDIc = {"user_id" : "001",
   #             "skill_level" : "1700"}
   
   #  data = json.dumps(testDIc)

   #  s.sendto(bytes(data,'utf8'), (serverIP, serverPort))

   #start thread
   #give funtion name and argument
   
   #start_new_thread(gameLoop, (s,))
   #start_new_thread(connectionLoop, (s,))
   #start_new_thread(cleanClients,(s,))
    while True:
        time.sleep(1)

if __name__ == '__main__':
   main()
