import subprocess
import re
import time
import platform

from Tetris.RenaTCPInterface import RenaTCPInterface

try:
    from pywinauto import Application
except ImportError:
    print("Could not import pywinauto! Have you run pip install pywinauto?")
    print("Pywinauto is not required and only for Windows but will allow you to switch Tetris panels if installed.")


def Set_Focus(number_to_focus):
    try:
        app = Application().connect(title_re="ARL A.I Tetris " + str(number_to_focus))
        dlg = app.top_window()
        dlg.set_focus()
        print("ARL A.I Tetris " + str(number_to_focus))
    except:
        print("Game " + str(number_to_focus) + " does not exist.")

def get_window_dialog_handle(number_to_focus):
    app = Application().connect(title_re="ARL A.I Tetris " + str(number_to_focus))
    dlg = app.top_window()
    return dlg

def StartGames():
    # Read config file
    config = open("Config.txt", "r")
    lines = config.readlines()
    games = int(re.search(r'\d+', lines[1]).group())

    # Change this to control how many times the game is run
    NumberOfTetrisGames = games
    # window_socket_ports = [9000 + i for i in range(games)]
    game_sockets = dict()
    game_dialog = dict()

    for Count in range(NumberOfTetrisGames):
        # if  platform.system() == "Windows":
        #     print("The program has detected that you are running Windows and will run the appropriate command to spool up Tetris games.")
        #     time.sleep(1)
        #     subprocess.Popen(".\Tetris.cpython-39.pyc " + str(Count) , shell=True)
        # else:
        #     print("The program has detected that you are running Linux or Mac and will run the appropriate command to spool up Tetris games.")
        #     time.sleep(1)
        #     subprocess.Popen("python Tetris.py " + str(Count) , shell=True)
        time.sleep(1)
        process = subprocess.Popen("python Tetris.py " + str(Count), shell=True)

        # establish TCP sockets
        game_sockets[Count] = (this_socket:=RenaTCPInterface(stream_name='RENA_SCRIPTING_INPUT',
                                             port_id=process.pid,
                                             identity='client',
                                             pattern='router-dealer'))
        this_socket.send_string('Go')  # send an empty message, this is for setting up the routing id

        game_dialog[Count] = get_window_dialog_handle(Count)
    # while True:
    #     # listen to the reward and auto switch windows
    #     pass

#StartGames()