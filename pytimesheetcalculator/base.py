import logging
import os
import six

from pytimesheetcalculator import config


LOG = logging.getLogger(__name__)


class BaseTimeSheetCalculator(object):
    """
    Common functionality between the multiple implementations
    """

    def __init__(self):
        self.config = config.Configuration()
        self.config.load()

        self.detect_max_length()

    def run(self, *args, **kwargs):
        raise NotImplementedError('Run Not Implemented by Base')

    def detect_max_length(self):
        max_len = 0
        for time_config in self.config.time_codes:
            max_len = max(max_len, len(time_config['name']))

        LOG.debug('Found max length of {0}'.format(max_len))
        self.config.runtime['options']['max_length'] = max_len

    def get_timecode_config(self, timecode_id):
        for time_code in self.config.time_codes:
            if time_code['id'] == timecode_id:
                return time_code

        LOG.error(
            '\n*** UNABLE TO FIND CONFIGURATION FOR TIME CODE: {0} ***\n'
            .format(
                timecode_id
            )
        )
        return None
