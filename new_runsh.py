#!/usr/bin/python3

import utils

def main():
    args = utils.parser_new_runsh()
    utils_utils = utils.Utils(args.appname)
    utils_utils.update_runsh(newrunsh=args.newrunsh)

if __name__ == "__main__":
    main()
    