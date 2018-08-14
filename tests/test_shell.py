from __future__ import print_function

import argparse
import json
import mock
import os
import tempfile

from pytimesheetcalculator import (
    base as calc_base,
    calculator,
    shell
)

import ddt

from tests import base


@ddt.ddt
class TestShell(base.TestBase):

    def setUp(self):
        super(TestShell, self).setUp()

    def tearDown(self):
        super(TestShell, self).tearDown()

    def test_invalid_json_input(self):
        with mock.patch('argparse.ArgumentParser') as mok_argparser:
            options_obj = mock.MagicMock()
            options_obj.time_sheet = 'foobar {'

            mok_argparser.parse_args = mock.MagicMock()
            mok_argparser.parse_args.return_value = options_obj

            exit_value = shell.main()
            self.assertEqual(exit_value, 2)

    @ddt.data(
        {'version': 'alpha'},
        {}
    )
    def test_invalid_document_version(self, version_data):
        encoded_version_data = json.dumps(version_data)
        config_file = tempfile.TemporaryFile()
        config_file.write(encoded_version_data.encode('utf-8'))
        config_file.seek(0, os.SEEK_SET)

        with mock.patch(
            'argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                time_sheet=config_file
            )
        ) as mok_argparser:
            exit_value = shell.main()
            self.assertEqual(exit_value, 1)

    def test_valid_document_version_ver2(self):
        version_data = {
            'version': '2'
        }
        encoded_version_data = json.dumps(version_data)
        config_file = tempfile.TemporaryFile()
        config_file.write(encoded_version_data.encode('utf-8'))
        config_file.seek(0, os.SEEK_SET)

        with mock.patch(
            'argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                time_sheet=config_file
            )
        ) as mok_argparser:
            with mock.patch(
                'pytimesheetcalculator.calculator.TimeSheetCalculator.run'
            ):
                with mock.patch(
                    'pytimesheetcalculator.config.Configuration'
                ) as mok_config:
                    mok_config.return_value = self.mock_config
                    exit_value = shell.main()
                    self.assertEqual(exit_value, 0)
