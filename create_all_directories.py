#!/usr/bin/python3

import utils

def main():
    args = utils.parser_appname_apptype()
    utils_utils = utils.Utils(appname=args.appname)
    utils_utils.create_all_directories(args.apptype)

if __name__ == "__main__":
    main()
    