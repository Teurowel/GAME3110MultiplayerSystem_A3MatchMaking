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

serverIP = "127.0.0.1"
#serverIP = "3.138.33.54"
serverPort = 12345

#list of user id in DataBase, {user_id : isInWaitingLobby}
listOfUserID = {"001" : False, "002" : False, "003" : False, "004" : False, "005" : False,
                "006" : False, "007" : False, "008" : False, "009" : False, "010" : False
               }

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


def UserRequestJoiningGame(sock) :
   # #######################First send connecting msg, server will add this client as new client######################
   # connectMsg = {"cmd" : "Connect",
   #               "user_id" : user_id}

   # jsonConnectMsg = json.dumps(connectMsg)
   # sock.sendto(bytes(jsonConnectMsg,'utf8'), (serverIP, serverPort))
   # ########################################################################

   #keep user joining game
   while True :
      for user_id in listOfUserID :
         #if this user is not in waitingLobby
         if listOfUserID[user_id] == False :
            #send match request
            connectMsg = {"cmd" : "Connect", "user_id" : user_id}
            jsonConnectMsg = json.dumps(connectMsg)
            sock.sendto(bytes(jsonConnectMsg,'utf8'), (serverIP, serverPort))

            #lock data
            clients_lock.acquire()

            listOfUserID[user_id] = True

            #release data
            clients_lock.release()

      time.sleep(1)

def main():
   #get number of game
   numOfGame = int(input("Number of game: "))

   #create sockect
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   
   connectMsg = {"cmd" : "StartSimulation"}
   jsonConnectMsg = json.dumps(connectMsg)
   sock.sendto(bytes(jsonConnectMsg,'utf8'), (serverIP, serverPort))

   #start thread that keep player requesting joining game
   start_new_thread(UserRequestJoiningGame, (sock,))

   #how many games are matched?
   matchedGameNum = 0

   #start requesting
   while True:
      #wait for reply from server
      data, addr = sock.recvfrom(1024)
      convertedData = json.loads(data)

      #check msg
      if convertedData["cmd"] == "MatchFoundResult" :
         if convertedData["Result"] == "Yes" :
            print("Match found")
            a = 10
            break
         else :
            print("Match not found, send next player for requesting")    

      #connection success msg  
      elif convertedData["cmd"] == "ConnectionSuccess" :
         print(convertedData["user_id"] + " connected!")

      #match found msg
      elif convertedData["cmd"] == "MatchFound" :
         print("Found match!")
         print("GameID: " + str(convertedData["gameID"]))
         
         for i in range(len(convertedData["users"])) :
            listOfUserID[convertedData["users"][i]["user_id"]] = False

         matchedGameNum += 1

      
      
      
      

   #Create socket, type of UDP

   #start multi thread, range will be player number, user_id will be player's unique user id
   #"{:03d}".format(user_id + 1) -> formating integer digit, 03d means change 0 -> 000, or 1 -> 001
   #  for user_id in range(5):
   #    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   #    start_new_thread(Client, (sock, "{:03d}".format(user_id + 1)))


   #  testDIc = {"user_id" : "001",
   #             "skill_level" : "1700"}
   
   #  data = json.dumps(testDIc)

   #  s.sendto(bytes(data,'utf8'), (serverIP, serverPort))

   #start thread
   #give funtion name and argument
   
   #start_new_thread(gameLoop, (s,))
   #start_new_thread(connectionLoop, (s,))
   #start_new_thread(cleanClients,(s,))

if __name__ == '__main__':
   main()

