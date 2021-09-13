#!/usr/bin/python3

import utils

def main():
    args = utils.parser_build_number()
    utils_utils = utils.Utils(None)
    utils_utils.build_number_decider(args.apptype, args.buildnumberweb,args.branch)
    print(utils_utils.get_jenkins_last_success_build_number)

if __name__ == "__main__":
    main()
    