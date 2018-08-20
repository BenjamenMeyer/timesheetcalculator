import mock

import ddt

from pytimesheetcalculator import base as calc_base

from tests import base


@ddt.ddt
class TestCommonBase(base.TestBase):

    def setUp(self):
        super(TestCommonBase, self).setUp()

    def tearDown(self):
        super(TestCommonBase, self).tearDown()

    @ddt.data(
        [],
        [{'name': 'abc'}],
        [{'name': 'cdefg'}, {'name': 'hijklmop'}]
    )
    def test_initialization(self, time_codes):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            self.mock_config.set_time_codes(time_codes)
            mok_config.return_value = self.mock_config

            instance = calc_base.BaseTimeSheetCalculator()

    def test_run_not_implemented(self):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config
            instance = calc_base.BaseTimeSheetCalculator()
            with self.assertRaises(NotImplementedError):
                instance.run()

    @ddt.data(
        ([], 0),
        ([{'name': 'abc'}], 3),
        ([{'name': 'cdefg'}, {'name': 'hijklmop'}], 8)
    )
    @ddt.unpack
    def test_detect_max_length(self, time_codes, expected_max_length):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            self.mock_config.set_time_codes(time_codes)
            mok_config.return_value = self.mock_config

            instance = calc_base.BaseTimeSheetCalculator()
            self.assertEqual(
                expected_max_length,
                instance.config.runtime['options']['max_length']
            )

    @ddt.data(
        ([], 'foobar', True),
        ([{'name': 'foo', 'id': 'bar'}], 'foobar', True),
        ([{'name': 'foo', 'id': 'bar'}], 'bar', False)
    )
    @ddt.unpack
    def test_get_timecode_config(self, time_codes, timecode_id, is_none):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            self.mock_config.set_time_codes(time_codes)
            mok_config.return_value = self.mock_config

            instance = calc_base.BaseTimeSheetCalculator()

            result = instance.get_timecode_config(timecode_id)
            if is_none:
                self.assertIsNone(result)
            else:
                for timecode in time_codes:
                    if timecode['id'] == timecode_id:
                        self.assertEqual(timecode, result)
                        break
