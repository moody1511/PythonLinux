#!/usr/bin/python3

import utils

def main():
    args = utils.parser_binary_update()
    utils_utils = utils.Utils(args.appname)
    utils_utils.move_new_web_to_folder(args.apptype, args.branch, args.buildnumber)

if __name__ == "__main__":
    main()
    