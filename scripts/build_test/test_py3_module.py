#!/usr/bin/python3

import sys
import importlib

def check_module_installed(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    arg = sys.argv[1]
    if arg.startswith("module="):
        module_name = arg[7:]
        is_installed = check_module_installed(module_name)
        print(is_installed)
    else:
        print("Invalid argument format. Please use: module=<module_name>")
