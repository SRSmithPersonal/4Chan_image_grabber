import requests
import os.path
import time
from datetime import date
from os import listdir
from io import open as iopen
from os import makedirs

Stop = True
Active = False
dir_path = ''


def set_stop():
    global Stop, Active
    Stop = True
    Active = False


def set_active():
    global Stop, Active
    Stop = False
    Active = True


def set_dirpath(pa):
    global dir_path
    dir_path = pa


# #Function to grab a list of all current 4Chan boards and their aliases, returns a list of tuples
def getBoards():
    adr = 'https://a.4cdn.org/boards.json'

    try:
        r = requests.get(adr)
        res = r.json()
    except Exception as e:
        print(e)

    boards = []

    for board in res["boards"]:
        boards.append((board["title"], board["board"]))

    return boards


# #Function that finds all threads on a board that have the given term/ phrase in there OP, then downloads all images
# #from those threads
def crawler(board, topic):
    print("Start Scrapping")
    adr = 'https://a.4cdn.org/{}/catalog.json'.format(board)

    # #Collect JSON data for board from 4chan API
    try:
        r = requests.get(adr)
        res = r.json()
    except Exception as e:
        print(e)

    # # make a list of threads that have the given term in their OP
    threadsy = []

    topic = topic.lower()

    for page in res:
        for thread in page["threads"]:
            if "com" in thread:
                if topic in thread["com"].lower():
                    threadsy.append(thread["no"])
                elif "sub" in thread:
                    if topic in thread["sub"].lower():
                        threadsy.append(thread["no"])
            elif "sub" in thread:
                if topic in thread["sub"].lower():
                    threadsy.append(thread["no"])

    print("Number of threads found: ", len(threadsy))

    # #Set path to save image files and create the directory if needed
    save_path = os.path.join(dir_path, "4chan/{}/{}".format(date.today(), topic))
    if not os.path.isdir(save_path):
        makedirs(save_path)

    # #List of files in directory
    files = listdir(save_path)

    # #For each thread found, the JSON data of that thread is collected, then each post is checked for attachments,
    # #which are then downloaded
    for thread in threadsy:
        if not Stop:
            jsonurl = "http://api.4chan.org/{}/res/{}.json".format(board, thread)

            try:
                r = requests.get(jsonurl)
                res = r.json()
            except Exception as e:
                print(e)

            for post in res["posts"]:
                if not Stop:
                    if ("filename" in post) and ("filedeleted" not in post):
                        file_name = "{}{}".format(post["tim"], post["ext"])
                        file_url = "http://i.4cdn.org/{}/{}".format(board, file_name)
                        # prevent grabbing the same post's image more than once
                        if file_name not in files:
                            re = requests.get(file_url)
                            complete_name = os.path.join(save_path, file_name)
                            with iopen(complete_name, 'wb') as file:
                                file.write(re.content)
                                file.close()

    print("Scrapping completed")


# #Function that performs a single scrapping run
def starter(listGrabs):
    global Active
    for search in listGrabs:
        if not Stop:
            crawler(search[0], search[1])
        else:
            print("stopping")
            break
    Active = False


# #Function that performs a scrapping run once every hour
def astarter(listGrabs):
    global Active
    while not Stop:
        for search in listGrabs:
            if not Stop:
                crawler(search[0], search[1])
            else:
                break

        for i in range(3600):
            if not Stop:
                time.sleep(1)
            else:
                print("stopping")
                break
    Active = False
