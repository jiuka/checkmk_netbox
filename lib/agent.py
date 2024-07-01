#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-License
#
# Copyright (C) 2023  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
import requests
from functools import cached_property

from cmk.special_agents.v0_unstable.agent_common import (
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser
)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGING = logging.getLogger('agent_netbox')


class AgentNetbox:
    '''Checkmk special Agent for Netbox'''

    def run(self):
        special_agent_main(self.parse_arguments, self.main)

    def parse_arguments(self, argv):
        parser = create_default_argument_parser(description=self.__doc__)

        parser.add_argument('-U', '--url',
                            dest='url',
                            required=True,
                            help='Rest API URL of the Netbox. (Example https://netbox.example.com/api)')
        parser.add_argument('-T', '--token',
                            dest='token',
                            required=True,
                            help='Netbox token.')
        parser.add_argument('-t', '--timeout',
                            dest='timeout',
                            required=False,
                            default=10,
                            help='HTTP connection timeout. (Default: 10)')
        parser.add_argument('--ignore-cert',
                            dest='verify_cert',
                            action='store_false',
                            help='Do not verify the SSL cert from the REST andpoint.')

        return parser.parse_args(argv)

    def main(self, args: Args):
        self.args = args

        self.section_scripts()
        self.section_data_sources()

    def section_scripts(self):
        with SectionWriter('netbox_script', separator=',') as writer:
            for script in self.scripts():
                try:
                    detail = self.get_job_detail(script)
                    if not detail:
                        writer.append(script['name'])
                        continue

                    writer.append(','.join([
                        script['name'],
                        '',
                        detail['status']['value'],
                        detail['completed'],
                    ]))

                    for test_name, test_result in detail['data'].get('tests', {}).items():
                        writer.append(','.join([
                            script['name'],
                            test_name,
                            detail['status']['value'],
                            detail['completed'],
                            str(test_result['info']),
                            str(test_result['success']),
                            str(test_result['warning']),
                            str(test_result['failure']),
                        ]))
                except Exception:
                    pass

    def scripts(self):
        url = '{}/extras/scripts/'.format(self.args.url)
        while url:
            response = self.client.get('{}/extras/scripts/'.format(self.args.url), timeout=self.args.timeout, verify=self.args.verify_cert)
            page = response.json()
            yield from page['results']
            url = page['next']

    def get_job_detail(self, job):
        params = dict(
            object_id=job['id'],
            completed__after='1970-01-01',
            limit=1,
            ordering='-completed',
        )
        response = self.client.get(f"{self.args.url}/core/jobs/", timeout=self.args.timeout, params=params, verify=self.args.verify_cert)
        if response.json()['results']:
            return response.json()['results'][0]
        return {}

    def section_data_sources(self):
        with SectionWriter('netbox_data_source') as writer:
            for data_source in self.get_data_sources():
                if 'last_synced' not in data_source:
                    detail = self.get_data_sources_detail(data_source)
                    data_source['last_synced'] = detail['completed']
                writer.append_json(dict(
                    name=data_source['name'],
                    description=data_source['description'],
                    enabled=data_source['enabled'],
                    status=data_source['status'],
                    last_synced=data_source['last_synced'],
                    file_count=data_source['file_count'],
                ))

    def get_data_sources(self):
        response = self.client.get('{}/core/data-sources/'.format(self.args.url), timeout=self.args.timeout, verify=self.args.verify_cert)
        return response.json()['results']

    def get_data_sources_detail(self, data_sorce):
        url = '{}/core/jobs/?object_id={}&completed__after=1970-01-01&ordering=-completed'.format(self.args.url, data_sorce['id'])
        while url:
            response = self.client.get(url, timeout=self.args.timeout, verify=self.args.verify_cert)
            page = response.json()
            for result in page['results']:
                if result['object_type'] == "core.datasource":
                    return result
            url = page['next']
        return {}

    @cached_property
    def client(self):
        c = requests.Session()
        c.headers.update({
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(self.args.token)
        })
        return c


if __name__ == '__main__':
    AgentNetbox().run()
