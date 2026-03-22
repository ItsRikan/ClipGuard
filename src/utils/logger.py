import logging
import os

path = os.path.join(os.getcwd(),"logfile.log")
logging.basicConfig(filename=path,level=logging.DEBUG,format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')