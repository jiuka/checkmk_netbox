#!/usr/bin/python
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

# <<<netbox_data_source>>>
# {"name": "test", "description": "test", "enabled": true, "status": {"value": "completed", "label": "Completed"}, "last_updated": "2023-05-03T13:13:29.965921+02:00", "file_count": 1}

from cmk.agent_based.v2 import (
    check_levels,
    Metric,
    render,
    Result,
    Service,
    State,
    AgentSection,
    CheckPlugin,
)

import json
from datetime import datetime


def parse_netbox_data_source(string_table):
    parsed = {}

    for line in string_table:
        data = json.loads(line[0])

        if 'last_synced' in data:
            data['last_synced'] = datetime.fromisoformat(data['last_synced']).replace(tzinfo=None)

        parsed[data['name']] = data

    return parsed


agent_section_netbox_data_source = AgentSection(
    name = "netbox_data_source",
    parse_function = parse_netbox_data_source,
)


def discovery_netbox_data_source(section):
    for name in section:
        yield Service(item=name)


def check_netbox_data_source(item, params, section):

    data_source = section[item]

    if data_source['status']['value'] == 'Failed':
        yield Result(state = State.CRIT, summary = f"Status is {data_source['status']['label']}")

    now = datetime.now()
    age = now - data_source['last_synced']
    yield from check_levels(
        value=age.total_seconds(),
        levels_upper=params.get('maxage', None),
        render_func=lambda f: render.timespan(f if f > 0 else -f),
        label='Last Sync' if age.total_seconds() > 0 else "Last Sync in",
    )

    yield Metric('file', data_source['file_count'])


check_plugin_netbox_data_source = CheckPlugin(
    name = "netbox_data_source",
    service_name = "Netbox DataSource %s",
    discovery_function = discovery_netbox_data_source,
    check_function = check_netbox_data_source,
    check_ruleset_name = "netbox_data_source",
    check_default_parameters = {'maxage': ('fixed', (2 * 24 * 3600, 7 * 24 * 3600))},
)
