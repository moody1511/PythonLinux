#!/usr/bin/python3

import argparse, requests, shutil, logging, sys, zipfile, os, subprocess, json, glob, socket, psycopg2, grp
from requests.adapters import HTTPAdapter
from telnetlib import Telnet
import urllib3


def parser_download_binary():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-branch', required='true', type=str, default='master'
    )
    args.add_argument(
        '-apptype', required='true', type=str
    )
    args.add_argument(
        '-download_dir', required='true', type=str
    )
    args.add_argument(
        '-buildnumber', type=str, default=None
    )
    return args.parse_args()

def parser_build_number():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-branch', required='true', type=str
    )
    args.add_argument(
        '-apptype', required='true', type=str
    )
    args.add_argument(
        '-buildnumberweb', type=str, default=None
    )
    return args.parse_args()

def parser_binary_update():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-appname', required='true', type=str
    )
    args.add_argument(
        '-branch', required='true', type=str
    )
    args.add_argument(
        '-apptype', required='true', type=str
    )
    args.add_argument(
        '-buildnumberweb', type=str, default=None
    )
    return args.parse_args()

def parser_default():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-appname', required='true', type=str
    )
    return args.parse_args()

def parser_cleanup():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-path',required=True,type=str
    )
    return args.parse_args()
def parser_dex_register():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-appname', required='true', type=str
    )
    args.add_argument(
        '-host', required='true', type=str
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

def parser_hostname():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-hostname', required='true', type=str
    )
    return args.parse_args()


def parser_appname_apptype():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-appname', required='true', type=str
    )
    args.add_argument(
        '-apptype', required='true', type=str
    )
    return args.parse_args()



def parser_new_runsh():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-appname', required='true', type=str
    )
    args.add_argument(
        '-sender', required='true', type=str
    )
    args.add_argument(
        '-newrunsh', required='true', type=str
    )
    return args.parse_args()

def parser_clean():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-path', required=True, type=str
    )
    return args.parse_args()

def parser_clean_directory():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-path', required=True, type=str
    )
    args.add_argument(
        '-left_files', type=int, default=5
    )
    args.add_argument(
        '-left_folders', type=int, default=5
    )
    return args.parse_args()


class Utils:
    def __init__(self, appname=None):
        self.appname = appname
        self.directory = "/opt/{}".format(appname)
        self.job_url_begin = "https://jenkins.ggniadekit.com/job/"
        self.job_url_end_last_success = "/lastSuccessfulBuild/artifact/*zip*/archive.zip"
        self.job_url_end_custom = "/artifact/*zip*/archive.zip"
        self.job_url_end_last_success_build_number = "/lastSuccessfulBuild/buildNumber"        
        self.init_logger()

    def init_logger(self):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('utils')

    def load_config(self, apptype=None):
        try:
            self.logger.info("Getting default variables for: {}".format(apptype))
            with open("app_vars/{}.json".format(apptype)) as config_file:
                self.loaded_config = json.load(config_file)
            config_file.close()
            self.logger.info("Got default variables for: {}".format(apptype))
        except:
            self.logger.error("Failed to get variables for: {}".format(apptype))
            raise

    def url_set(self, apptype=None, branch=None, buildnumber=None):
        try:
            self.logger.info("Setting download url")
            if buildnumber == None:
                self.url = self.job_url_begin + apptype + "-" + branch + buildnumber
            else:
                self.url = self.job_url_begin + apptype + "-" + branch + "/" + buildnumber + self.job_url_end_custom
        except:
            self.logger.error("Failed to setup download url")
            raise

    def check_if_download_is_require(self, download_dir, apptype, branch, buildnumber):
        try:
            if os.path.exists('{}/{}/archive-{}'.format(download_dir, apptype, buildnumber)):
                self.logger.info("Binary already in server, skipping download")
                return False
            else:
                for file_in_downloads in glob.glob('{}/{}/*'.format(download_dir, apptype)):
                    if branch + "-" + buildnumber in file_in_downloads:
                        self.logger.info("Binary already in server, skipping download")
                        return False
            self.logger.info("There is no binary in server, gonna start download")
            return True
        except:
            self.logger.error("Failed to check if download is required")
            raise

    def download_binary(self, apptype, download_dir):
        self.download_path_archive = "{}/{}/{}".format(download_dir, apptype, "archive.zip")
        try:
            self.logger.info("Start downloading: {}".format(self.url))
            command = "/usr/bin/wget -O {} --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 0 --continue {}".format(self.download_path_archive, self.url)
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            p.wait()
            self.logger.info("Finished downloading: {}".format(self.url))
        except:
            self.logger.error("Failed to download: {}".format(self.url))
            raise

    def unzip_archive_zip_file_and_move_to_downloads(self, apptype, download_dir):
        try:
            self.logger.info("Start unziping {}".format(self.download_path_archive))
            with zipfile.ZipFile(self.download_path_archive,"r") as zip_ref:
                self.logger.info("Unziping to {}/archive".format(self.download_path_archive))
                zip_ref.extractall("{}/archive".format(self.download_path_archive.replace("/archive.zip", "")))                    
            zip_ref.close()
            self.logger.info("Unziped {}".format(self.download_path_archive))
            self.logger.info("Moving jar to: {} from archive".format("/opt/tools/downloads/{}/".format(apptype)))
            for file_to_move in glob.glob("{}/{}/{}".format(download_dir, apptype, self.loaded_config["unzip_download_jar_location"])):
                shutil.copy(file_to_move, "/opt/tools/downloads/{}/".format(apptype))
                self.logger.info("Moved jar to: {} from archive".format("/opt/tools/downloads/{}/".format(apptype)))
        except:
            self.logger.error("Failed unziping {}".format(self.download_path_archive))
            raise


    def cleanup(self,clean_item=None):
        try:
            if ".zip" in clean_item or ".jar" in clean_item or ".rar" in clean_item:
                self.logger.info("Deleted {}".format(clean_item))
                os.remove(clean_item)
            else:
                self.logger.info("Deleted {}".format(clean_item))
                shutil.rmtree(clean_item)
        except FileNotFoundError:
            self.logger.error("Failed to delete {}".format(clean_item))
            raise

    def cleanup_directory(self,path=None):
        try:
            for directory_object in os.listdir(path):
                directory_path = os.path.join(path,directory_object)
                if ".zip" in directory_path or ".jar" in directory_path or ".rar" in directory_path:
                    if os.path.isfile(directory_path) or os.path.islink(directory_path):
                        self.logger.info("Deleted {}".format(directory_path))
                        os.remove(directory_path)
        except FileNotFoundError:
            self.logger.error("Failed to delete {}".format(directory_path))
            raise

    def deletefiles(self,path=None,days=None):
        try:
            dir_path=(path)
            all_files = os.listdir(path)
            now = time.time()
            n=1+(days)
            n_days = n  * 86400
            for f in all_files:
                file_path = os.path.join(dir_path, f)
                if ".zip" in file_path or ".jar" in file_path or ".rar" in file_path:
                        if os.stat(file_path).st_mtime <= now - (n_days):
                            os.remove(file_path)
                            print("Deleted ", f)
        except FileNotFoundError:
            raise

    def deletefilesrecursive(self,path=None,days=None):
        try:
            now = time.time()
            n=1+(days)
            n_days = n * 86400
            for directory_object in os.listdir(path):
                directory_path = os.path.join(path,directory_object)
                if os.path.isfile(directory_path) or os.path.islink(directory_path):
                    if os.stat(directory_path).st_mtime <= now - (n_days):
                        if ".zip" in directory_path or ".jar" in directory_path or ".rar" in directory_path:
                            os.remove(directory_path)
                            print("Deleted ", directory_path)
                else:
                    shutil.rmtree(directory_path)
        except FileNotFoundError:
            raise

    def deleteoldest(self,path=None,delete_oldest=None):
        try:
            for filename in sorted(os.listdir(path))[:-(delete_oldest)]:
                filename_relPath = os.path.join(path,filename)
                print(filename_relPath)
                os.remove(filename_relPath)
        except FileNotFoundError:
            raise

    def deleteoldestreverse(self,path=None,delete_oldest=None):
        try:
            for filename in sorted(os.listdir(path),reverse=True)[:-(delete_oldest)]:
                filename_relPath = os.path.join(path,filename)
                print(filename_relPath)
                os.remove(filename_relPath)
        except FileNotFoundError:
            raise

    def clean(self, clean_item=None):
        try:
            self.logger.info("Start clean up: {}".format(clean_item))
            if ".zip" in clean_item or ".jar" in clean_item or ".js" in clean_item:
                os.remove(clean_item)
            else:
                shutil.rmtree(clean_item)
            self.logger.info("Finished clean up: {}".format(clean_item))
        except FileNotFoundError:
            self.logger.info("Nothing to clean: {}".format(clean_item))
        except:
            self.logger.error("Failed clean up: {}".format(clean_item))
            raise

    def clean_up_directory(self, path=None, left_files=5):
        try:
            self.logger.info("Cleaning up directory: {}".format(path))
            files = list(filter(os.path.isfile, glob.glob(path)))
            files.sort(key=os.path.getmtime)
            if len(files) > left_files:
                for file_to_delete in files[0:len(files)-left_files]:
                    if ".zip" in file_to_delete or ".jar" in file_to_delete or ".js" in file_to_delete:
                        os.remove(file_to_delete)
                    else:
                        shutil.rmtree(file_to_delete)
                    self.logger.info("Removed: {}".format(file_to_delete))        
                self.logger.info("Finished clean up directory: {}".format(path))
            else:
                self.logger.info("Nothing to clear, leaving: {}".format(path))
        except:
            self.logger.error("Failed clean up directory: {}".format(path))
            raise
        
    def clean_up_folders(self, path=None, left_folders=5):
        try:
            self.logger.info("Cleaning up directory: {}".format(path))
            dirs = list(filter(os.path.isdir, glob.glob(path)))
            dirs.sort(key=os.path.getmtime)
            if len(dirs) > left_folders:
                for dirs_to_delete in dirs[0:len(dirs)-left_folders]:
                    shutil.rmtree(dirs_to_delete)
                    self.logger.info("Removed: {}".format(dirs_to_delete))        
                self.logger.info("Finished clean up directory: {}".format(path))
            else:
                self.logger.info("Nothing to clear, leaving: {}".format(path))
        except:
            self.logger.error("Failed clean up directory: {}".format(path))
            raise

    def backup_old_web(self):
        try:
            self.logger.info("Backup {}".format(self.directory))
            subprocess.call('cp -r {}/package.json {}/dist/* {}/backup'.format(self.directory, self.directory, self.directory), shell=True)
            self.logger.info("Finished backup {}".format(self.directory))
        except:
            self.logger.error("Failed backup {}".format(self.directory))
            raise

    def build_number_decider(self, apptype=None, build_number_web=None, branch=None):
        if build_number_web == None:
            last_success_build_number = self.job_url_begin + apptype + "-" + branch + self.job_url_end_last_success_build_number
            self.get_jenkins_last_success_build_number = requests.get(last_success_build_number).text
        else:
            self.get_jenkins_last_success_build_number = str([i for i in [build_number_web] if i][0])

    def move_new_web_to_folder(self, apptype, branch, buildnumber):
        try:
            self.load_config(apptype)
            self.logger.info("Moving new .jar to {}".format(self.directory))
            for file_to_move in glob.glob("/opt/tools/downloads/{}/*".format(apptype)):
                if  branch + "-" + buildnumber in file_to_move:
                    self.logger.info("Moving {} to {}".format(file_to_move, "{}".format(self.directory)))
                    shutil.copy("{}".format(file_to_move), "{}".format(self.directory))
                    self.logger.info("Moved new .jar to {}".format(self.directory))
        except:
            self.logger.error("Failed to move new .jar {}".format(self.directory))
            raise


    def update_runsh(self, newrunsh):
        try:
            self.logger.info("Updating run.sh for: {}".format(self.appname))
            with open("{}/run.sh".format(self.directory), "w") as runsh:
                runsh.write(newrunsh)
            runsh.close()
            self.logger.info("Updated run.sh for: {}".format(self.appname))
        except:
            self.logger.error("Failed to update run.sh for: {}".format(self.appname))
            raise

    def create_all_directories(self, apptype):
        try:
            self.logger.info("Creating directories for: {}".format(self.appname))
            self.load_config(apptype)
            for directory in self.loaded_config['directories']:
                if not os.path.exists(directory.replace("{{ folder }}", self.appname)):
                    os.makedirs(directory.replace("{{ folder }}", self.appname))

            log_directory = self.directory + "/log"
            if not os.path.exists(log_directory):
                os.symlink("/var/log/exchange/{}".format(self.appname), log_directory)

            if not os.path.exists(log_directory + '/start_stop.txt'):
                open(log_directory + '/start_stop.txt', 'a').close()
                os.chmod(log_directory + '/start_stop.txt', 0o666)

                self.logger.info("Created directories for: {}".format(self.appname))
        except:
            self.logger.error("Failed to create directories for: {}".format(self.appname))
            raise

    def get_hostip(self, host):
        return socket.gethostbyname(host)


    def setup_web(self, host):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__)) 
            self.setup_template(current_directory + "/templates/web.conf", "conf/application.conf")
            self.setup_template(current_directory + "/templates/web.start.sh", "start.sh")
            self.setup_template(current_directory + "/templates/web.stop.sh", "stop.sh")
            self.setup_template(current_directory + "/templates/web.run.sh", "run.sh") 
            self.prepare_start_and_stop_sh()
            self.prepare_run_sh_web(host=host)
            self.create_systemd()
        except:
            self.logger.error("Failed to setup web templates")
            raise

    def prepare_run_sh_web(self, host):
        self.replace_on_start_or_stop_or_run_sh("run.sh", "{{ host }}", host)
        os.chmod("{}/run.sh".format(self.directory), 0o775)
        exchange_id = os.getuid()
        groupinfo = grp.getgrnam('runsh')
        os.chown("{}/run.sh".format(self.directory), exchange_id, groupinfo[2])


    def prepare_start_and_stop_sh(self):
        self.replace_on_start_or_stop_or_run_sh("start.sh", "{{ folder }}", self.appname)
        self.replace_on_start_or_stop_or_run_sh("stop.sh", "{{ folder }}", self.appname)
        os.chmod("{}/start.sh".format(self.directory), 0o775)
        os.chmod("{}/stop.sh".format(self.directory), 0o775)
        exchange_id = os.getuid()
        groupinfo = grp.getgrnam('startstop')
        os.chown("{}/start.sh".format(self.directory), exchange_id, groupinfo[2])
        os.chown("{}/stop.sh".format(self.directory), exchange_id, groupinfo[2])

    def replace_on_start_or_stop_or_run_sh(self, script_name, old_string, new_string):
        self.logger.info("Prepare config for app {}".format(script_name))
        with open("{}/{}".format(self.directory, script_name), "r") as script:
            script_read = script.read()
            script_read = script_read.replace(old_string, new_string)
        script.close()
        with open("{}/{}".format(self.directory, script_name), "w") as script:
            script.write(script_read)
        script.close()

    def setup_template(self, template, conf_name):
        self.logger.info("Setup template {}".format(conf_name))
        with open(template, "r") as template:
            template_read = template.read()
        template.close()
        with open("{}/{}".format(self.directory, conf_name), "w") as template:
            template.write(template_read)
        template.close()
          

    def create_systemd(self):
        try:
            self.logger.info("Setting up systemd")
            p = subprocess.Popen(["/usr/bin/sudo /opt/installservice.sh {}".format(self.appname)], stdout=subprocess.PIPE, shell=True, executable='/bin/sh')
            p_status = p.communicate()
            self.logger.info("Set up systemd")
        except:
            self.logger.exception("Failed to setup systemd {}".format(self.appname))




