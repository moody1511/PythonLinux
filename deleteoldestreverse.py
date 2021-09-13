#!/usr/bin/python3

import utils

def main():
    args = utils.parser_cleanupdirectory()
    utils_utils = utils.Utils()
    utils_utils.deleteoldestreverse(path=args.path,delete_oldest=args.delete_oldest)
    
if __name__ == "__main__":
    main()