import mock

import ddt

from pytimesheetcalculator import (
    base as calc_base,
    calculator
)

from tests import base


@ddt.ddt
class TestCalculator(base.TestBase):

    def setUp(self):
        super(TestCalculator, self).setUp()

    def tearDown(self):
        super(TestCalculator, self).tearDown()

    def test_instantiation(self):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            obj = calculator.TimeSheetCalculator()
            self.assertIsInstance(obj, calc_base.BaseTimeSheetCalculator)
            self.assertEqual(obj.time_data, {})

    def test_run(self):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            with mock.patch(
                'pytimesheetcalculator.calculator.TimeSheetCalculator.'
                'apply_timesheet_options'
            ):
                with mock.patch(
                    'pytimesheetcalculator.calculator.TimeSheetCalculator.'
                    'detect_active_hours'
                ):
                    with mock.patch(
                        'pytimesheetcalculator.calculator.TimeSheetCalculator.'
                        'calculate_hours'
                    ):
                        with mock.patch(
                            'pytimesheetcalculator.calculator.'
                            'TimeSheetCalculator.'
                            'display'
                        ):
                            with mock.patch(
                                'pytimesheetcalculator.calculator.'
                                'TimeSheetCalculator.'
                                'display_available_codes'
                            ):
                                with mock.patch(
                                    'pytimesheetcalculator.calculator.'
                                    'TimeSheetCalculator.'
                                    'display_date_summaries'
                                ):
                                    mok_config.return_value = self.mock_config

                                    obj = calculator.TimeSheetCalculator()
                                    obj.run({})

    @ddt.data(
        (
            {},
            {'active_hours': 168, 'max_length': 0}
        ),
        (
            {'options': {}},
            {'active_hours': 168, 'max_length': 0}
        ),
        (
            {'options': {'other_option': ''}},
            {'active_hours': 168, 'max_length': 0}),
        (
            {'options': {'total_hours': 40}},
            {'active_hours': 40, 'max_length': 0}
        ),
        (
            {'options': {'Total_Hours': 80}},
            {'active_hours': 80, 'max_length': 0}
        ),
    )
    @ddt.unpack
    def test_apply_timesheet_options(self, json_doc, applied_options):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            default_runtime_options = {
                'active_hours': 168,
                'max_length': 0
            }

            obj = calculator.TimeSheetCalculator()
            # parent detects max length and adds option
            self.assertEqual(
                obj.config.runtime['options'],
                default_runtime_options
            )

            obj.apply_timesheet_options(json_doc)
            self.assertEqual(
                obj.config.runtime['options'],
                applied_options
            )

    @ddt.data(
        ({'dates': {}}, {}),
        ({'dates': {"foobar": {'jobs': []}}}, {}),
        ({'dates': {"barfoo": {'jobs': [{'hours': 0}]}}}, {}),
        ({'dates': {"barfoo": {'jobs': [{'id': 'world', 'hours': 28}]}}}, {})
    )
    @ddt.unpack
    def test_detect_active_hours_empty_cases(self, json_doc, applied_options):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config
            obj = calculator.TimeSheetCalculator()
            obj.detect_active_hours(json_doc)
            self.assertEqual(
                obj.config.runtime['options']['active_hours'],
                self.mock_config.default_active_hours
            )

    def test_detect_active_hours_noncounting_hours(self):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            self.mock_config.time_codes = [
                {
                    "name": "Active but uncounted time",
                    "id": "happy_hour",
                    "active": True,
                    "counts_on_40": False
                },
                {
                    "name": "Active and counted",
                    "id": "fantasy_island",
                    "active": True,
                    "counts_on_40": True,
                }
            ]
            mok_config.return_value = self.mock_config

            discounted_hours = 8
            json_doc = {
                "dates": {
                    "m3g3t0ky0": {
                        "jobs": [
                            {
                                "id": "happy_hour",
                                "hours": discounted_hours,
                                "description": "ph34r th3 b33r"
                            },
                            {
                                "id": "fantasy_island",
                                "hours": 35,
                                "description": "ph34r th3 b33r"
                            },
                        ]
                    }
                }
            }

            obj = calculator.TimeSheetCalculator()
            self.assertEqual(
                obj.config.runtime['options']['active_hours'],
                self.mock_config.default_active_hours
            )
            obj.detect_active_hours(json_doc)
            self.assertEqual(
                obj.config.runtime['options']['active_hours'],
                (self.mock_config.default_active_hours - discounted_hours)
            )

    @ddt.data(
        (
            {'dates': {}},
            {
                'total_hours': 0,
                'total_percentage': 0.0,
                'date_hours': {},
                'job_hours': {}
            }
        ),
        (
            {'dates': {'freebie': {'jobs': []}}},
            {
                'total_hours': 0,
                'total_percentage': 0.0,
                'date_hours': {
                    'freebie': {
                        'total_hours': 0,
                        'jobs': []
                    }
                },
                'job_hours': {}
            }
        )
    )
    @ddt.unpack
    def test_calculate_hours_empty(self, json_doc, expected_time_data):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config
            obj = calculator.TimeSheetCalculator()
            obj.calculate_hours(json_doc)
            self.assertEqual(
                obj.time_data,
                expected_time_data
            )

    def test_calculate_hours_multidoc(self):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config
            json_doc = {
                'dates': {
                    'freebie': {
                        'jobs': []
                    }
                }
            }
            expected_time_data = {
                'total_hours': 0,
                'total_percentage': 0.0,
                'date_hours': {
                    'freebie': {
                        'total_hours': 0,
                        'jobs': []
                    }
                },
                'job_hours': {}
            }

            obj = calculator.TimeSheetCalculator()
            obj.calculate_hours(json_doc)
            obj.calculate_hours(json_doc)
            self.assertEqual(
                obj.time_data,
                expected_time_data
            )

    @ddt.data(
        (
            {
                'dates': {
                    'freebie': {'jobs': [{'id': 'foobar'}]}
                }
            },
            {
                'total_hours': 0,
                'total_percentage': 0.0,
                'date_hours': {
                    'freebie': {
                        'total_hours': 0,
                        'jobs': []
                    }
                },
                'job_hours': {}
            }
        )
    )
    @ddt.unpack
    def test_calculate_no_time_code_config(self, json_doc, expected_time_data):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config
            obj = calculator.TimeSheetCalculator()
            obj.calculate_hours(json_doc)
            self.assertEqual(
                obj.time_data,
                expected_time_data
            )

    @ddt.data(
        (
            {
                'dates': {
                    'foils': {
                        'jobs': [
                            {'id': 'foobar', 'hours': 8, 'description': 'foo'}
                        ]
                    }
                }
            },
            {
                'total_hours': 8,
                'total_percentage': 0.0,
                'date_hours': {
                    'foils': {
                        'total_hours': 8,
                        'jobs': [
                            {'id': 'foobar', 'hours': 8, 'description': 'foo'}
                        ]
                    }
                },
                'job_hours': {
                    'foobar': {
                        'hours': 8,
                        'percentage': 0.0
                    }
                }
            }
        )
    )
    @ddt.unpack
    def test_calculate_invalid_timecode_config_for_jobhour_calc(
        self, json_doc, expected_time_data
    ):
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            with mock.patch(
                'pytimesheetcalculator.calculator.TimeSheetCalculator'
                '.get_timecode_config'
            ) as mok_get_timecode:
                mok_get_timecode.side_effect = [
                    {'id': 'foobar', 'counts_on_40': True, 'active': True},
                    None
                ]

                obj = calculator.TimeSheetCalculator()
                obj.config.runtime['options']['active_hours'] = 8
                obj.calculate_hours(json_doc)
                self.maxDiff = None
                self.assertEqual(
                    obj.time_data,
                    expected_time_data
                )

    @ddt.data(
        (
            {
                'dates': {
                    'foils': {
                        'jobs': [
                            {'id': 'foobar', 'hours': 8, 'description': 'foo'},
                            {'id': 'foobar', 'hours': 8, 'description': 'bar'},
                            {
                                'id': 'd34db33f',
                                'hours': 8,
                                'description': 'foobar'
                            }
                        ]
                    }
                }
            },
            {
                'total_hours': 16,
                'total_percentage': 100.0,
                'date_hours': {
                    'foils': {
                        'total_hours': 24,
                        'jobs': [
                            {'id': 'foobar', 'hours': 8, 'description': 'foo'},
                            {'id': 'foobar', 'hours': 8, 'description': 'bar'},
                            {
                                'id': 'd34db33f',
                                'hours': 8,
                                'description': 'foobar'
                            }
                        ]
                    }
                },
                'job_hours': {
                    'd34db33f': {
                        'hours': 8,
                        'percentage': 0.0
                    },
                    'foobar': {
                        'hours': 16,
                        'percentage': 100.0
                    }
                }
            }
        )
    )
    @ddt.unpack
    def test_calculate_valid_timecode_config_for_jobhour_calc(
        self, json_doc, expected_time_data
    ):
        self.mock_config.time_codes.append(
            {
                "name": "FooBar",
                "id": "foobar",
                "active": True,
                "counts_on_40": True
            }
        )
        self.mock_config.time_codes.append(
            {
                "name": "DeadBeef",
                "id": "d34db33f",
                "active": True,
                "counts_on_40": False
            }
        )
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            obj = calculator.TimeSheetCalculator()
            obj.config.runtime['options']['active_hours'] = 16
            obj.calculate_hours(json_doc)
            self.maxDiff = None
            self.assertEqual(
                obj.time_data,
                expected_time_data
            )

    @ddt.data(
        True, False
    )
    def test_display(self, match_total_hours):
        self.mock_config.time_codes = [
            {
                "name": "FooBar",
                "id": "foobar",
                "active": True,
                "counts_on_40": True
            },
            {
                "name": "BarFoo",
                "id": "barfoo",
                "active": True,
                "counts_on_40": True
            },
        ]
        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            obj = calculator.TimeSheetCalculator()
            obj.time_data = {
                'total_hours': (
                    self.mock_config.default_active_hours
                    if match_total_hours
                    else 10
                ),
                'total_percentage': 55.0,
                'job_hours': {
                    'foobar': {
                        'hours': 8,
                        'percentage': 50.0
                    },
                    'barfoo': {
                        'hours': 0,
                        'percentage': 0.0
                    },
                    'bar': {
                        'hours': 8,
                        'percentage': 0.0
                    }
                }
            }
            obj.display()
            # technically `print` could be mocked up and the output compared to
            # some expected output; however, what's output doesn't matter too
            # much - it's more about the logic.

    def test_display_available_codes(self):
        self.mock_config.time_codes = [
            {
                "name": "Bar",
                "id": "bar",
                "active": True,
                "counts_on_40": True,
            },
            {
                "name": "FooBar",
                "id": "foobar",
                "active": True,
                "counts_on_40": True,
            },
            {
                "name": "BarFoo",
                "id": "barfoo",
                "active": False,
                "counts_on_40": True
            }
        ]

        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            obj = calculator.TimeSheetCalculator()
            obj.time_data = {
                'total_hours': 8,
                'total_percentage': 55.0,
                'job_hours': {
                    'foobar': {
                        'hours': 8,
                        'percentage': 50.0
                    },
                    'barfoo': {
                        'hours': 0,
                        'percentage': 0.0
                    },
                    'foo': {
                        'hours': 50,
                        'percentage': 25.0
                    }
                }
            }
            obj.display_available_codes()
            # technically `print` could be mocked up and the output compared to
            # some expected output; however, what's output doesn't matter too
            # much - it's more about the logic.

    def test_display_date_summaries(self):
        self.mock_config.time_codes = [
            {
                "name": "Bar",
                "id": "bar",
                "active": True,
                "counts_on_40": True,
            },
            {
                "name": "FooBar",
                "id": "foobar",
                "active": True,
                "counts_on_40": True,
            },
            {
                "name": "BarFoo",
                "id": "barfoo",
                "active": False,
                "counts_on_40": True
            }
        ]

        with mock.patch(
            'pytimesheetcalculator.config.Configuration'
        ) as mok_config:
            mok_config.return_value = self.mock_config

            obj = calculator.TimeSheetCalculator()
            obj.time_data = {
                'total_hours': 8,
                'total_percentage': 55.0,
                'date_hours': {
                    'bardate': {
                        'total_hours': 5.0,
                        'jobs': [
                            {
                                'name': 'foo',
                                'id': 'foobar',
                                'description': 'feed me',
                                'hours': 5
                            },
                            {
                                'name': 'bad foo',
                                'id': 'foo',
                                'description': 'seymour',
                                'hours': 6
                            }
                        ]
                    }
                }
            }
            obj.display_date_summaries()
            # technically `print` could be mocked up and the output compared to
            # some expected output; however, what's output doesn't matter too
            # much - it's more about the logic.
