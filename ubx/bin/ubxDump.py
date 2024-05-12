import argparse
import sys
import os

import ubx

def cli():
    parser = argparse.ArgumentParser(
                    prog="ubxdump",
                    description="Decode UBX packets from file or stdin and dump to terminal.")
    parser.add_argument("file", nargs="?", default=sys.stdin.buffer, help="File to read from. Reads from stdin if no file supplied.")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()

def main():
    args = cli()
    
    # Open file if necessary
    if(args.file != sys.stdin.buffer):
        if(not os.path.isfile(args.file)):
            print("%s is not a file." % args.file)
        args.file = open(args.file, mode="rb")

    # Read in and parse chunks
    n = 1024

    chunk = args.file.read(n)
    data = chunk
    while chunk:
        start = data.find(b"\xb5\x62")
        if start == -1:
            chunk = args.file.read(n)
            data = chunk
            continue
        
        # Get more data if not whole header
        if (len(data) - start) < 6:
            chunk = args.file.read(n)
            data += chunk
            continue

        msgClass, msgID, msgLen = ubx.msgInfo(data[start : start + 6])
        end = start + 6 + msgLen + 2
        
        if end > len(data):
            chunk = args.file.read(n)
            data += chunk
            continue

        print(ubx.getMsgName(msgClass, msgID))

        if(args.verbose):
            print(ubx.parseMsg(data[start:end]))

        data = data[end:]