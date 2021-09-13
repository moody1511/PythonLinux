#!/usr/bin/python3

import utils

def main():
    args = utils.parser_appname_host_hostip()
    utils_utils = utils.Utils(appname=args.appname)
    utils_utils.setup_web(host=args.host)

if __name__ == "__main__":
    main()
    