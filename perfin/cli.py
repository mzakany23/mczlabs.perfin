#!/usr/local/bin/python3
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("perfin cli")
    parser.add_argument("-f", help="load a file by path", action="append")
    args = parser.parse_args()

    if args.f:
        print(args.f)
