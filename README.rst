PyTimeSheetCalculator
---------------------

PyTimeSheetCalculator is a basic utility for working with tracking one's own time.
It provides the ability to record a daily time log for given tasks and display the
weekly percentage of time worked and daily summaries.

.. note:: PyTimeSheetCalculator uses a JSON file to store timesheet information.
    It does not enforce that the file be explicitly compliant with what it expects
    - that is, one can add additional fields without breaking PyTimeSheetCalculator.

Configuration
-------------

PyTimeSheetCalculator is configured via a file stored in either of the following locations:

    - /etc/cws/timesheets.json
    - ~/.config/cws/timesheets.json

The configuration file looks like the following:

.. code-block:: json

    {
    "options": {
        "default_total_hours": 40
    },
    "codes": [
            {
                "name": "Descriptive Name for the user",
                "id": "unique job id code",
                "active": <boolean>,
                "counts_on_40": <boolean>
            },
            ...
        ]
    }
  
The `name` and `id` fields are basic text fields.

The `active` field is a boolean value for whether or not the job/task code can be actively used.
If it is not to be actively used then a warning is given if it is used.

The `counts_on_40` field is a boolean value for whether time charged against the code counts towards official time values.
If a job/task does not count, then its hours are subtracted from the total hours so that the percentage without it still
reflects a 100% total. For example, if vacation time is not recorded then the value for a vacation time code would be set to False so that the
total hours are reduced by that amount.

Time Sheets
-----------

A JSON file is used to store time sheet data, and looks like the following:

.. code-block:: json

    {
        "version": "2",
        "dates": {
            "yyyy-mm-dd": {
                "jobs": [
                    {
                    "id": "unique job id code from configuration",
                    "hours": <# of hours charged>,
                    "description": "description of the work done"
                    },
                    ...
                ]
            },
            ...
        }
    }

.. note:: The version information is important. If it is missing then the file format might not be supported.

.. note:: The version `1` file format is no longer supported.
