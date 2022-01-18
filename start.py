#!/usr/bin/env -S python -B
import argparse
from client import TcpipClient
from otsuki import OtsukiAgent

if __name__ == "__main__":
    agent = OtsukiAgent()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-p", type=int, action="store", dest="port")
    parser.add_argument("-h", type=str, action="store", dest="hostname")
    parser.add_argument("-r", type=str, action="store", dest="role", default="none")
    parser.add_argument("-n", type=str, action="store", dest="name", default="otsuki")
    input_args = parser.parse_args()
    TcpipClient(agent, input_args.name, input_args.hostname, input_args.port, input_args.role).connect()
