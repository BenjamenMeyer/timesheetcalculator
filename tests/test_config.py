import mock
import os
import six

import ddt

from pytimesheetcalculator import config

from tests import base


@ddt.ddt
class TestConfig(base.TestBase):

    def setUp(self):
        super(TestConfig, self).setUp()
        self.os_environ_home = os.environ.get('HOME', '')

    def tearDown(self):
        super(TestConfig, self).tearDown()
        os.environ['HOME'] = self.os_environ_home

    def test_instantiation(self):
        obj = config.Configuration()
        self.assertEqual(obj.data, {})

    @ddt.data(
        ('runtime', 'foobar', {}),
        ('runtime', 'barfoo', {'runtime': {}}),
        ('options', 'dead', {}),
        ('options', 'b33f', {'options': {}}),
        ('time_codes', '2b2b', {}),
        ('time_codes', 'd4d4', {'codes': {}}),
    )
    @ddt.unpack
    def test_attributes(self, attr_name, attr_value, default_dict):
        obj = config.Configuration()
        obj.data = default_dict

        setattr(obj, attr_name, attr_value)
        self.assertEqual(
            attr_value,
            getattr(obj, attr_name)
        )
        

    @ddt.data(
        ({'runtime': {}, 'options': {}}, None),
        ({'runtime': {}, 'options': {}}, '/home/foo'),
        ({'runtime': {}, 'options': {'default_total_hours': 200}}, '/home/bar'),
    )
    @ddt.unpack
    def test_load(self, config_data, user_home_dir):
        mok_open_path = (
            'builtins.open'
            if six.PY3
            else '__builtin__.open'
        )
        mok_open_obj = mock.mock_open()
        with mock.patch(mok_open_path, new_callable=mok_open_obj) as mok_open:
            with mock.patch('json.load') as mock_json_load:
                mock_json_load.return_value = config_data

                config_location = '/etc/cws/timesheets.json'
                if user_home_dir:
                    os.environ['HOME'] = user_home_dir
                    config_location = '{0}/.config/cws/timesheets.json'.format(
                        user_home_dir
                    )
                else:
                    if 'HOME' in os.environ:
                        del os.environ['HOME']

                obj = config.Configuration()

                obj.load()
                self.assertEqual(mok_open.call_count, 1)
                mok_open.assert_called_with(config_location, 'r')
                self.assertEqual(obj.data, config_data)
                self.assertIn('options', obj.runtime)
                self.assertIn('max_length', obj.runtime['options'])
                self.assertEqual(0, obj.runtime['options']['max_length'])
                self.assertIn('active_hours', obj.runtime['options'])
                self.assertEqual(
                    config_data['options'].get('default_total_hours', 40),
                    obj.runtime['options']['active_hours']
                )
