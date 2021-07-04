#!/usr/bin/python3

import utils

def main():
    args = utils.parser_cleanupdirectory()
    utils_utils = utils.Utils()
    utils_utils.deletefiles(path=args.path,days=args.days)
    
if __name__ == "__main__":
    main()