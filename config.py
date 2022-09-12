import logging
import configmap
import os

confmap = configmap.Config("configfiles/", ["config.yaml"])
confmap.load_config()
config = confmap.config
if os.getenv('LOCAL'):
# if 1 == 1:
    confmap = configmap.Config("configfiles/", ["local_config.yaml"])
    confmap.load_config()
    config = confmap.local_config

logging.basicConfig(format=config.log.format, level=config.log.level)
