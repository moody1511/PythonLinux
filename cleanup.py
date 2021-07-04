#!/usr/bin/python3

import utils

def main():
    args = utils.parser_cleanup()
    utils_utils = utils.Utils()
    utils_utils.cleanup(clean_item=args.path)

if __name__ == "__main__":
    main()