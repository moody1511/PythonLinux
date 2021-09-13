#!/usr/bin/python3

import utils

def main():
    args = utils.parser_default()
    utils_utils = utils.Utils(args.appname)
    utils_utils.backup_old_web()

if __name__ == "__main__":
    main()