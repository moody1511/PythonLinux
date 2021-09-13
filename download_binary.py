#!/usr/bin/python3

import utils

def main():
    args = utils.parser_download_binary()
    utils_utils = utils.Utils()
    utils_utils.load_config(args.apptype)
    if utils_utils.check_if_download_is_require(args.download_dir, args.apptype, args.branch, args.buildnumber):
        utils_utils.url_set(apptype=args.apptype, 
                            branch=args.branch,
                            buildnumber=args.buildnumber)
        utils_utils.download_binary(args.apptype, args.download_dir)
        utils_utils.unzip_archive_zip_file_and_move_to_downloads(args.apptype, args.download_dir, args.buildnumber)

if __name__ == "__main__":
    main()
