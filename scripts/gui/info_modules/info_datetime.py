#!/usr/bin/python3
import datetime

def show_info():

    return str(datetime.datetime.now()).split(".")[0]


if __name__ == '__main__':
    print(show_info())
