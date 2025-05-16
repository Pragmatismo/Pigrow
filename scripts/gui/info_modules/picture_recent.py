#!/usr/bin/python3
import os
homedir = os.getenv("HOME")


def show_info():
    caps_path = os.path.join(homedir, "Pigrow", "caps")
    if not os.path.isdir(caps_path):
        return "none"

    # get a sorted list of all entries in caps_path
    files = sorted(os.listdir(caps_path))

    # define which extensions count as "images"
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}

    # scan from the end; return the first image we find
    for fname in reversed(files):
        ext = os.path.splitext(fname)[1].lower()
        if ext in image_exts:
            return os.path.join(caps_path, fname)

    return "none"

if __name__ == '__main__':
    print(show_info())
