import random
import socket
import time

#from _thread import all(*)
from _thread import *
import threading

from threading import Thread

from datetime import datetime
import json

#for requesting user info from AWSLamda
import requests

#For data synchoronize
clients_lock = threading.Lock()

serverIP = "127.0.0.1"
#serverIP = "3.138.33.54"
serverPort = 12345

#list of user id in DataBase, {user_id : isInWaitingLobby}
listOfUserID = {"001" : False, "002" : False, "003" : False, "004" : False, "005" : False,
                "006" : False, "007" : False, "008" : False, "009" : False, "010" : False
               }

def UpdateUserInfoToAWSLamda(user) :
   #make body for AWSLamda
   body = {"user_id" : user["user_id"], "skill_level" : user["skill_level"]}

   #request put to update user info
   resp = requests.put("https://6w26z2v5vj.execute-api.us-east-2.amazonaws.com/default/UpdatePlayerInfo", data = json.dumps(body) )
   respBody = json.loads(resp.content)
   
   print(respBody["user_id"] + " updated")

#users is array of dictionary{"user_id", "skill_level", "name"}
def GameSimulation(convertedData) :
   users = convertedData["users"]
   gameID = convertedData["gameID"]
   gameStartedTime = convertedData["gameStartedTime"]

   #randomly select winner among 3users
   winnerIdx = random.randint(0, 2)
   loseUser1Idx = -1
   loseUser2Idx = -1

   #set lose user idx
   if winnerIdx == 0 :
      loseUser1Idx = 1
      loseUser2Idx = 2
   elif winnerIdx == 1 :
      loseUser1Idx = 0
      loseUser2Idx = 2
   elif winnerIdx == 2 :
      loseUser1Idx = 0
      loseUser2Idx = 1

   #from ELO rating system
   KFactor = 30

   #log user's skill level before game
   skillLevelline = "SkillLevel : {}({}), {}({}), {}({})\n".format(users[0]["user_id"], int(users[0]["skill_level"]), 
                                                                   users[1]["user_id"], int(users[1]["skill_level"]),
                                                                   users[2]["user_id"], int(users[2]["skill_level"]))

   
   #calculate sum of all matched users skill level
   sumOfAllUserSkillLevel = 0
   for i in range(3) :
      sumOfAllUserSkillLevel += int(users[i]["skill_level"])

   #(1 - (winner skill level / sum of skill levels)) * KFactor
   winnerPoint = (1 - (int(users[winnerIdx]["skill_level"]) / sumOfAllUserSkillLevel)) * KFactor
   winnerPoint = round(winnerPoint)

   #(0 - (lose skill level / sum of skill levels)) * KFactor
   losePoint1 = (0 - (int(users[loseUser1Idx]["skill_level"]) / sumOfAllUserSkillLevel)) * KFactor
   losePoint1 = round(losePoint1)

   losePoint2 = (0 - (int(users[loseUser2Idx]["skill_level"]) / sumOfAllUserSkillLevel)) * KFactor
   losePoint2 = round(losePoint2)

   #update user's skill level
   users[winnerIdx]["skill_level"] = str(int(users[winnerIdx]["skill_level"]) + winnerPoint)
   UpdateUserInfoToAWSLamda(users[winnerIdx])

   users[loseUser1Idx]["skill_level"] = str(int(users[loseUser1Idx]["skill_level"]) + losePoint1)
   UpdateUserInfoToAWSLamda(users[loseUser1Idx])

   users[loseUser2Idx]["skill_level"] = str(int(users[loseUser2Idx]["skill_level"]) + losePoint2)
   UpdateUserInfoToAWSLamda(users[loseUser2Idx])

   print("Wirte game result to log file")

   #open log text file
   f = open("GameLog.txt","a+")

   #write game id
   f.write("GameID : %d\n" % gameID)

   #write game started time
   f.write("GameStartedTime : %s\n" % gameStartedTime)
   
   #write each user's Id and connected time
   userIDline = "UserID(ConnectedTime) : {}({}), {}({}), {}({})\n".format(users[0]["user_id"], users[0]["connectedTime"], 
                                                                          users[1]["user_id"], users[1]["connectedTime"],
                                                                          users[2]["user_id"], users[2]["connectedTime"])
   f.write(userIDline)

   #write user's skill level
   f.write(skillLevelline)

   #write game result
   gameResultLine = "GameResult : Winner: {}, Loser: {}, {}\n".format(users[winnerIdx]["user_id"], 
                                                                      users[loseUser1Idx]["user_id"],
                                                                      users[loseUser2Idx]["user_id"])
   f.write(gameResultLine)

   skillLevelAfterGameLine = "SkillLevelAfterGame : {}({}), {}({}), {}({})\n".format(users[0]["user_id"], int(users[0]["skill_level"]), 
                                                                                     users[1]["user_id"], int(users[1]["skill_level"]),
                                                                                     users[2]["user_id"], int(users[2]["skill_level"]))
   f.write(skillLevelAfterGameLine)

   f.write("\n")
   f.close()

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
   #start_new_thread(UserRequestJoiningGame, (sock,))

   userRequestJoiningGameThread = Thread(target=UserRequestJoiningGame, args=(sock,))
   userRequestJoiningGameThread.start()

   #how many games are matched?
   matchedGameNum = 0

   #create empty log file
   print("Create GameLog file")
   f = open("GameLog.txt","w+")
   f.close()

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
         print("Users: " + convertedData["users"][0]["user_id"] + " " + convertedData["users"][1]["user_id"] + " " + convertedData["users"][2]["user_id"])
         #simulate game using matched users
         GameSimulation(convertedData)

         for i in range(len(convertedData["users"])) :
            #lock data
            clients_lock.acquire()

            listOfUserID[convertedData["users"][i]["user_id"]] = False

            #release data
            clients_lock.release()

         matchedGameNum += 1

         if(matchedGameNum == numOfGame) :
            print("All game done, finish Simulation Script")
            break

   #wait until this thread finish   
   userRequestJoiningGameThread.join()  
   
   #shutdown socket
   sock.shutdown(socket.SHUT_RDWR)
   sock.close()
      

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

