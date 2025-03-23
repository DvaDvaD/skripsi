import multiprocessing
import psutil
import math
import docker
import os



DOCKER_CLIENT = docker.from_env()
DOCKER_PREFIX = "dr-"
DB_FILENAME = 'results.db'
CODE_COVERAGE_PATH = '/code-coverage'


# Print welcoe ASCII art
def welcome():
    print(" ____              _____ _____ _____ _____ \n|    \\ ___ ___ ___| __  |   __|   __|_   _|\n|  |  | -_| -_| . |    -|   __|__   | | |  \n|____/|___|___|  _|__|__|_____|_____| |_|  \n              |_|                          ")
    print("Welcome to the DeepREST experiment infrastructure.")

def get_apis():
    return os.listdir('./apis')

def get_tools():
    return os.listdir('./tools')