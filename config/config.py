import json
import os
import collections
import numpy as np


class Configuration(object):

    @staticmethod
    def load(path, name):
        with open(os.path.join(path, "{}.json".format(name)), 'r') as f:
            return Configuration(json.load(f))

    @staticmethod
    def merge(**configurations):
        _config = Configuration({})
        for key in configurations:
            _config[key] = configurations[key]
        return _config

    def __init__(self, config):
        if isinstance(config, collections.Iterable):
            self.config = config
        else:
            self.config = {}

    def __getitem__(self, key):
        if isinstance(key, str):
            segments = key.split(".")
            part = self.config
            for segment in segments:
                if segment in part:
                    part = part[segment]
                else:
                    raise KeyError(
                        segment, '{} not a valid key in {}'.format(segment, key))
            return part
        else:
            if len(key) == 2 and key[1] is True:
                return self.choice(key[0])
            else:
                raise TypeError(key, 'Wrong type of key:', type(key))

    def __str__(self):
        return self.config.__str__()

    def save(self, path, name):
        with open(os.path.join(path, "{}.json".format(name)), 'w+') as f:
            json.dump(self.config, f)

    def default(self, prop, defaultValue=''):
        try:
            return self[prop]
        except KeyError:
            return defaultValue

    def choice(self, key):
        return np.random.choice(self[key]) if isinstance(self[key], (list,)) else self[key]

    def __call__(self, name='Configuration', keyLen=20, valueLen=30):
        totalLen = (keyLen + valueLen + 1)
        divider = '-' * totalLen
        print(divider)
        print(divider)
        print(('{:^' + str(totalLen) + '}').format(name))
        print(divider)
        print(divider)
        self._print_self(keyLen, valueLen, self.config, '', divider=divider)

    def _print_self(self, keyLen=20, valueLen=30, obj={}, prefix='', divider=None):
        act_prefix = "{} ".format(prefix) if prefix != '' else ''
        for key in obj:
            if type(obj[key]) is dict:
                print(self._str_pair('{}{}'.format(
                    act_prefix, key), '', keyLen, valueLen))
                self._print_self(keyLen, valueLen, obj[key], prefix + '-')
            else:
                print(self._str_pair('{}{}'.format(
                    act_prefix, key), obj[key], keyLen, valueLen))
            if divider is not None:
                print(divider)

    def _str_pair(self, key, val, keyLen, valueLen, seperator=' '):
        return ('{:<' + str(keyLen) + '}{}{:<' + str(valueLen) + '}').format(str(key), str(seperator), str(val))

    def __setitem__(self, key, value):
        if isinstance(key, str):
            segments = key.split(".")
            part = self.config
            for segment in segments[:-1]:
                if segment not in part:
                    part[segment] = {}
                if type(part[segment]) is not dict:
                    part[segment] = {}
                part = part[segment]

            part[segments[-1]] = value

            return part
        else:
            raise TypeError(key, 'Wrong type of key')


if __name__ == "__main__":
    conf = Configuration(
        {"hello": "world", "list": [500, 24, 37], "single": 100})

    print(conf["hello"])
    print(conf.choice("list"))
    print(conf.choice("single"))
    print(conf["hello", True])
    print(conf["list", True])
    print(conf["list"])
