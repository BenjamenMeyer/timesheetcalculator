import argparse
import json
import sys

from pytimesheetcalculator import calculator


def main():
    argument_parser = argparse.ArgumentParser(
        description="Time Sheet Calculator"
    )
    argument_parser.add_argument(
        '--time-sheet', '-ts',
        default=None,
        type=argparse.FileType('rt'),
        required=True,
        help=(
            'JSON file containing a dictionary of time code ids and '
            'hours worked'
        )
    )
    arguments = argument_parser.parse_args()
    try:
        data = arguments.time_sheet.read()
        json_doc = json.loads(data)

    except Exception as e:
        print('Invalid JSON input document: %s - %s' % (e, data))
        return 2

    # input document versions matching up to the class managing it
    tsc_versions = {
        '2': calculator.TimeSheetCalculator
    }

    try:
        # version 1 document doesn't have the version field in it
        json_doc_version = json_doc['version']
    except KeyError:
        json_doc_version = '1'

    try:
        tsc_used = tsc_versions[json_doc_version]
    except KeyError:
        print(
            "Unknown input document version {0}. Supported versions: {1}"
            .format(
                json_doc_version,
                tsc_versions.keys()
            )
        )
        return 1

    tsc = tsc_used()
    tsc.run(json_doc)

    return 0
