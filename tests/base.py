from unittest import TestCase


class MockConfig(object):

    def __init__(self):
        self.default_active_hours = 168
        self.data = {
            'runtime': {
                'options': {
                    'active_hours': self.default_active_hours
                }
            },
            'options': {},
            'codes': [] 
        }

    def set_time_codes(self, time_codes):
        self.data['codes'] = time_codes

    def load(self):
        pass

    @property
    def runtime(self):
        return self.data['runtime']

    @runtime.setter
    def runtime(self, value):
        self.data['runtime'] = value

    @property
    def options(self):
        return self.data['options']

    @options.setter
    def options(self, value):
        self.data['options'] = value

    @property
    def time_codes(self):
        return self.data['codes']

    @time_codes.setter
    def time_codes(self, value):
        self.data['codes'] = value


class TestBase(TestCase):

    def setUp(self):
        super(TestBase, self).setUp()
        self.mock_config = MockConfig()

    def tearDown(self):
        super(TestBase, self).tearDown()
