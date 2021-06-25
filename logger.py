'''
Created on Jun 4, 2021

@author: 869259
'''
import os
import logging
from configparser import ConfigParser, ExtendedInterpolation
from logging.handlers import RotatingFileHandler
import configparser

this_file_path = os.path.abspath(os.path.dirname(__file__))
conf_file = os.path.join(this_file_path, 'pythonconfig.ini')
config = ConfigParser(interpolation=ExtendedInterpolation())
# config = configparser.ConfigParser()
config.read(conf_file)

#config = ConfigParser(interpolation=ExtendedInterpolation())
#config_file_path = os.path.dirname(os.path.realpath(__file__))
#conf = config.read(os.path.join(config_file_path,'pythonconfig.ini'))


log_path = config.get("Path", "app_log_path")
sales_order_file_path = config.get("local_file_path","sales_order_data")
wrp_file_path = config.get("local_file_path","wrp_data")
max_log_bytes = int(config.get("app_log", "max_log_bytes"))
log_backups = int(config.get("app_log", "backups"))
log_format = config.get("app_log", "format")
LOG_LEVEL = int(config.get("app_log", "log_level"))
medium = config.get("fetch_source", "medium")
sql_driver = config.get("db_details","sql_driver")
server_address = config.get("db_details","server_address")
db_name = config.get("db_details","db_name")
sql_driver = config.get("db_details","sql_driver")
uid = config.get("db_details","uid")
pwd = config.get("db_details","pwd")

try:
    if os.path.isdir(log_path):
        print("log_path available, log creating in app_log_path",log_path)
    else:
        os.mkdir(log_path)
        print("app_log_path unavailable, trying to create new directory")
except:
    print("creating log in current working directory")
    log_path = os.getcwd()

file_name = os.path.join(log_path,config.get("app_log", "logfile"))
print(file_name)
def logging_func():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(log_format)
    HANDLER = RotatingFileHandler(file_name,  maxBytes=max_log_bytes, backupCount=log_backups)
    HANDLER.setFormatter(formatter)
    logger.addHandler(HANDLER)
    logger.setLevel(LOG_LEVEL)
    return logger
# logger=logging_func()