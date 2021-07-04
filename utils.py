#!/usr/bin/python3

import argparse, requests, shutil, logging, sys, zipfile,os,subprocess, json, glob, socket, psycopg2, grp,time,datetime
from requests.adapters import HTTPAdapter 
from telnetlib import Telnet
import urllib3

def parser_cleanup():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-path',required=True,type=str
    )
    return args.parse_args()

def parser_cleanupdirectory():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-path',required=True,type=str
    )
    args.add_argument(
        '-days',type=int,metavar='',default=1,help='Delete files older than (Default: %(default)s) days'
    )
    args.add_argument(
        '-delete_oldest',type=int,metavar='',default=1,help='Delete files and save (Default: %(default)s) oldest '
    )
    return args.parse_args()


class Utils:
#Usuwanie pojedyńczych plików z koncówką .zip / .jar /.rar
    def cleanup(self,clean_item=None):
        try:
            if ".zip" in clean_item or ".jar" in clean_item or ".rar" in clean_item:
                os.remove(clean_item)
            else:
                shutil.rmtree(clean_item)
        except FileNotFoundError:
            raise
#Usuwanie plików rekursywnie z folderów
    def cleanup_directory(self,path=None):
        try:
            for directory_object in os.listdir(path):
                directory_path = os.path.join(path,directory_object)
                if ".zip" in directory_path or ".jar" in directory_path or ".rar" in directory_path:
                    if os.path.isfile(directory_path) or os.path.islink(directory_path):
                        print(directory_path)
                        os.remove(directory_path)
                    else:
                        shutil.rmtree(directory_path)
        except FileNotFoundError:
            raise

#Usuwanie najnowszych plików z datą
    def deletefiles(self,path=None,days=None):
        try:
            dir_path=(path)
            all_files = os.listdir(path)
            now = time.time()
            n=(days)
            n_days = n  * 86400
            for f in all_files:
                file_path = os.path.join(dir_path, f)
                if ".zip" in file_path or ".jar" in file_path or ".rar" in file_path:
                        if os.stat(file_path).st_mtime >= now - (n_days):
                            print(now)
                            print(os.stat(file_path).st_mtime)
                            #os.remove(file_path)
                            print("Deleted ", f)
        except FileNotFoundError:
            raise

#Usuwanie plikow z data rekursywnie z folderow
    def deletefilesrecursive(self,path=None,days=None):
        try:
            now = time.time()
            n=(days)
            n_days = n * 86400
            for directory_object in os.listdir(path):
                directory_path = os.path.join(path,directory_object)
                if os.path.isfile(directory_path) or os.path.islink(directory_path):
                    os.remove(directory_path)
                    print("Deleted ", directory_path)
                else:
                    shutil.rmtree(directory_path)
        except FileNotFoundError:
            raise
#Usuwanie najnowszych plików zostawiając stare
    def deleteoldest(self,path=None,delete_oldest=None):
        try:
            for filename in sorted(os.listdir(path))[:-(delete_oldest)]:
                filename_relPath = os.path.join(path,filename)
                os.remove(filename_relPath)
        except FileNotFoundError:
            raise
