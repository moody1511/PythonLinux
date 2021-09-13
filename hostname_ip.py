#!/usr/bin/python3

import utils

def main():
    args = utils.parser_hostname()
    utils_utils = utils.Utils()
    ip = utils_utils.get_hostip(host=args.hostname)
    print(ip)

if __name__ == "__main__":
    main()
