import logging
import os
import re

import yaml
from easydict import EasyDict
import inotify.adapters
from twisted.internet import defer, reactor, threads
from typing import Any


class Config:
    def __init__(self, path, files, on_load=None):
        self.inotify = inotify.adapters.Inotify()
        self.path = path
        self.files = files
        self.on_load = on_load
        self.log = logging.getLogger()
        self.log.setLevel("INFO")

    def load_config(self, load_name=None):
        """
        Загрузить все файлы или указанный
        :param load_name:
        """
        for name in self.files:
            if load_name is not None and name != load_name:
                continue
            self.log.debug(f"Load configfile '{name}'")
            with open(f"{self.path}{name}") as file:
                _config = yaml.safe_load(file)
            cfg = EasyDict(_config)
            replace_env(cfg)
            setattr(self, name.split('.')[0], cfg)
            if self.on_load is not None:
                self.on_load(name, cfg)

    @defer.inlineCallbacks
    def observer(self):
        """
        Запустить слежение за папкой, использует reactor
        """
        event_generator = self.inotify.event_gen()
        while True:
            try:
                event = yield threads.deferToThread(next, event_generator)
            except StopIteration:
                break
            if event is None:
                break
            (header, type_names, watch_path, filename) = event
            self.log.debug(f"inotify event={event}")
            # локально отслеживаем IN_CLOSE_WRITE на сервере ждём IN_MOVED_TO
            if type_names == ['IN_MOVED_TO'] or type_names == ['IN_CLOSE_WRITE']:
                yield threads.deferToThread(self.load_config)
        reactor.callLater(15, self.observer)

    def add_watch(self):
        self.inotify.add_watch(self.path)
        reactor.callLater(15, self.observer)

    def remove_watch(self):
        self.inotify.remove_watch(self.path)


def replace_env(node: Any):
    """
    Замена переменных окружения в тексте конфигурационного файла
    :param node: Any
    """
    try:
        if isinstance(node, EasyDict):
            for k, v in node.items():
                v, r = replace_env(v)
                if r:
                    node[k] = v
            return node, False
        elif isinstance(node, list):
            for i, n in enumerate(node):
                v, r = replace_env(n)
                if r:
                    node[i] = v
            return node, False
        elif isinstance(node, str):
            found = False
            value = node
            for env in re.findall(r"\$\w+", node):
                val = os.environ.get(env[1:], None)
                if val is not None:
                    value = value.replace(env, val)
                    found = True
            return value, found
        else:
            return node, False
    except Exception as err:
        raise err
