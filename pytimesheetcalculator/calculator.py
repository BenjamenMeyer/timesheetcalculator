import logging
import six

from pytimesheetcalculator import base


LOG = logging.getLogger(__name__)


class TimeSheetCalculator(base.BaseTimeSheetCalculator):
    '''
    This version upgrades the original functionality by tracking by-day instead
    of overall thereby making it easy to validate hours/day. Moreover, it drops
    the support for comments while adding the ability to provide descriptions
    for each day's work time. Each day is a simple list of job codes and time.

    Some of the detected information that was previously scanned for is now in
    its own section, and an explicit version section was added.

    Timesheet input:

        {
            "version": "2",
            "dates": {
                "<date>": {
                    "jobs": [
                        {
                            "id": <job_id>,
                            "hours": <hours>,
                            "description": "comment value"
                        }
                    ]
                },
            },
            "options": {
                "total_hours": <total>,
            }
        }
    '''

    def __init__(self):
        super(TimeSheetCalculator, self).__init__()
        self.time_data = {}

    def run(self, json_doc):
        self.apply_timesheet_options(json_doc)
        self.detect_active_hours(json_doc)
        self.calculate_hours(json_doc)
        self.display()
        self.display_available_codes()
        self.display_date_summaries()

    def apply_timesheet_options(self, json_doc):
        if 'options' in json_doc:
            for option_name, option_value in six.iteritems(
                json_doc['options']
            ):
                if option_name.lower() == 'total_hours':
                    print(
                        "*** Adjusting Default Active Hours from {0} to {1}"
                        .format(
                            self.config.runtime['options']['active_hours'],
                            option_value
                        )
                    )
                    self.config.runtime[
                        'options']['active_hours'] = option_value

    def detect_active_hours(self, json_doc):
        for job_date, data in six.iteritems(json_doc['dates']):
            for jobs_on_date in data['jobs']:
                if jobs_on_date['hours']:
                    job_config = self.get_timecode_config(jobs_on_date['id'])
                    if job_config is None:
                        continue

                    if not job_config['counts_on_40']:
                        self.config.runtime[
                            'options']['active_hours'] -= jobs_on_date['hours']

    def calculate_hours(self, json_doc):
        # if time_data is empty, configure it
        # NOTE: This will only be untrue if the multiple documents
        #   are processed by the same instance.
        if not self.time_data:
            LOG.debug('Initializing time data...')
            self.time_data = {
                'total_hours': 0,
                'total_percentage': 0.0,
                'date_hours': {},
                'job_hours': {}
            }
        for job_date, data in six.iteritems(json_doc['dates']):
            LOG.debug('Processing {0} - {1}'.format(job_date, data))
            # if the date is not present, configure it
            # NOTE: This will only be untrue if the multiple documents
            #   are processed by the same instance.
            if job_date not in self.time_data['date_hours']:
                LOG.debug('Initializing job date {0}'.format(job_date))
                self.time_data['date_hours'][job_date] = {
                    'total_hours': 0,
                    'jobs': []
                }

            for jobs_on_date in data['jobs']:
                LOG.debug('Date Processing: job {0}'.format(jobs_on_date))
                job_id = jobs_on_date['id']
                job_config = self.get_timecode_config(job_id)
                if job_config is None:
                    LOG.debug(
                        'Date Processing: Job ID {0} has no '
                        'configuration'.format(
                            job_id
                        )
                    )
                    continue

                LOG.debug(
                    'Date Processing: JOB ID {0} - Configuration {1}'.format(
                        job_id,
                        job_config
                    )
                )

                hours = jobs_on_date['hours']
                if job_config['counts_on_40']:
                    LOG.debug(
                        'Date Processing: Adding {0} to job'.format(
                            hours
                        )
                    )
                    self.time_data['total_hours'] += hours

                self.time_data['date_hours'][job_date]['total_hours'] += hours
                self.time_data['date_hours'][job_date]['jobs'].append(
                    jobs_on_date
                )

                if job_id not in self.time_data['job_hours']:
                    LOG.debug(
                        'Date Processing: Adding {0} to job_hours with '
                        '{1} hours'.format(
                            job_id,
                            hours
                        )
                    )
                    self.time_data['job_hours'][job_id] = {
                        'hours': hours,
                        'percentage': 0.0
                    }
                else:
                    LOG.debug(
                        'Date Processing: Updating {0} in job_hours with {1}'
                        ' hours from {2} to {3}'.format(
                            job_id,
                            hours,
                            self.time_data['job_hours'][job_id]['hours'],
                            (
                                self.time_data[
                                    'job_hours'][job_id]['hours'] + hours
                            )
                        )
                    )
                    self.time_data['job_hours'][job_id]['hours'] += hours

        for job_id, job_hours in six.iteritems(self.time_data['job_hours']):
            # since the `self.time_data` is populated above then the
            # data should be curated and it should be impossible to get
            # an invalid job_id
            LOG.debug('Job Processing: job id: {0}'.format(job_id))
            LOG.debug(
                'Job Processing: time codes: {0}'.format(
                    self.config.time_codes
                )
            )
            hours_job_config = self.get_timecode_config(job_id)
            if hours_job_config is None:
                continue

            if hours_job_config['counts_on_40']:
                LOG.debug('Job Processing: job counts towards work hours')
                job_hours['percentage'] = (
                    (
                        float(job_hours['hours']) / self.config.runtime[
                            'options']['active_hours']
                    ) * 100.0
                )

                LOG.debug(
                    'Job Processing: Job Percentage {0}'.format(
                        job_hours['percentage']
                    )
                )
                LOG.debug(
                    'Job Processing: Update total percentate from {0} by {1}'
                    ' to {2}'.format(
                        self.time_data['total_percentage'],
                        job_hours['percentage'],
                        (
                            self.time_data[
                                'total_percentage'] + job_hours['percentage']
                        )
                    )
                )
                self.time_data['total_percentage'] += job_hours['percentage']
                LOG.debug(
                    'Job Processing: Time Data - {0}'.format(
                        self.time_data
                    )
                )

    def display(self):
        for job_id in sorted(self.time_data['job_hours'].keys()):
            job_config = self.get_timecode_config(job_id)
            if job_config is None:
                continue

            v = self.time_data['job_hours'][job_id]['hours']
            p = self.time_data['job_hours'][job_id]['percentage']
            if v:
                print(
                    "{0:<80}{1:>8}{2:>9}{3}".format(
                        job_config['name'],
                        '{0:2,.2f}'.format(v),
                        '{0:2,.2f}'.format(p),
                        '' if job_config['active']
                        else '\tWARNING IN ACTIVE CODE IN USE'
                    )
                )

        print(
            "\n{0:>73}Total: {1:>8}{2:>9}".format(
                '',
                '{0:2,.2f}'.format(self.time_data['total_hours']),
                '{0:2,.2f}'.format(self.time_data['total_percentage'])
            )
        )

        if (
            self.time_data['total_hours'] != self.config.runtime[
                'options']['active_hours']
        ):
            print(
                '\nWARNING: Total Hours DO NOT MATCH\n'
                '\tCalculated Total: {0:2,.2f}'
                '\t    Active Total: {1:2,.2f}'
                .format(
                    self.time_data['total_hours'],
                    self.config.runtime['options']['active_hours']
                )
            )

    def display_available_codes(self):
        print("\nAvailable Time Codes:")
        all_job_ids = [
            time_code['id']
            for time_code in self.config.time_codes
        ]
        LOG.debug('All Time Codes: {0}'.format(all_job_ids))

        for job_id in self.time_data['job_hours'].keys():
            if self.time_data['job_hours'][job_id]['hours']:
                if job_id in all_job_ids:
                    all_job_ids.remove(job_id)
                    LOG.debug('Removing Job ID: {0}'.format(job_id))

        LOG.debug('Final Time Codes: {0}'.format(all_job_ids))

        for job_id in sorted(all_job_ids):
            job_config = self.get_timecode_config(job_id)
            LOG.debug(
                'Job ID {0} Configuration: {1}'.format(
                    job_id,
                    job_config
                )
            )

            # .. note:: Since all_jobs_ids is built from the source for
            #   get_timecode_config is should be impossible to not get a
            #   config here for the job_id.

            if job_config and job_config['active']:
                print("\t{0} (id: {1})".format(job_config['name'], job_id))

    def display_date_summaries(self):
        print("\nDate Summary:")
        for date_key in sorted(self.time_data['date_hours'].keys()):
            data = self.time_data['date_hours'][date_key]
            print(
                "\t{0} - Total hours: {1}".format(
                    date_key,
                    data['total_hours']
                )
            )
            for job_on_date in data['jobs']:
                job_config = self.get_timecode_config(job_on_date['id'])
                if job_config:
                    print(
                        '\t\t{0:<80}{1:>8} "{2:}"'.format(
                            job_config['name'],
                            job_on_date['hours'],
                            job_on_date['description']
                        )
                    )
