import json
import logging
import os


LOG = logging.getLogger(__name__)


class Configuration(object):

    __ATTR_RUNTIME__ = 'runtime'
    __ATTR_OPTIONS__ = 'options'
    __ATTR_TIME_CODES__ = 'codes'

    def __init__(self):
        self.data = {}

    def load(self):
        user_home = os.environ.get('HOME')
        config_location = None
        config_filename = 'timesheets.json'
        if user_home:
            config_location = '{0}/.config/cws/{1}'.format(
                user_home, config_filename
            )
        else:
            config_location = '/etc/cws/{0}'.format(config_filename)

        LOG.debug('Config File: {0}'.format(config_location))
        with open(config_location, 'r') as config_input:
            self.data = json.load(config_input)
            # add section for run-time config options
            self.runtime = {
                'options': {
                    'max_length': 0,
                    'active_hours': self.options.get('default_total_hours', 40)
                }
            }

    @property
    def runtime(self):
        return self.data.get(self.__ATTR_RUNTIME__, {})

    @runtime.setter
    def runtime(self, value):
        self.data[self.__ATTR_RUNTIME__] = value

    @property
    def options(self):
        return self.data.get(self.__ATTR_OPTIONS__, {})

    @options.setter
    def options(self, value):
        self.data[self.__ATTR_OPTIONS__] = value

    @property
    def time_codes(self):
        return self.data.get(self.__ATTR_TIME_CODES__, [])

    @time_codes.setter
    def time_codes(self, value):
        self.data[self.__ATTR_TIME_CODES__] = value
