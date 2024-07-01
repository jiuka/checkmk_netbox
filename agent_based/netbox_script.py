#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-License
#
# Copyright (C) 2023-2024  Marius Rieder <marius.rieder@scs.ch>
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

# <<<netbox_script>>>
# dellos6.DellOS6Report,DellOS6Report,test_device
# dellos6.DellOS6Report,DellOS6Report,test_interface
# devices.DeviceConnectionsReport,DeviceConnectionsReport,test_power_connections
# dhcp.DhcpReport,DhcpReport,test_pool_is_in_prefix,2023-01-04T08:00:01.134531+01:00,0,0,41,0
# dhcp.DhcpReport,DhcpReport,test_prefix_has_pool,2023-01-04T08:00:01.134531+01:00,0,0,41,0
# ipam.IpAddressReport,IpAddressReport,test_name_or_description,2022-12-22T14:20:32.555035+01:00,0,23,0,0
# ipam.PrefixReport,PrefixReport,test_broadcast_reservation,2022-12-21T16:01:17.599839+01:00,0,0,101,0
# ipam.PrefixReport,PrefixReport,test_no_subprefix_in_active,2022-12-21T16:01:17.599839+01:00,0,1,100,0

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

from datetime import datetime


def parse_netbox_script(string_table):
    parsed = {}

    for line in string_table:
        script = parsed.setdefault(line[0], dict(name=line[0]))

        if len(line) > 3:
            script.update(dict(
                state=line[2],
                last_run=datetime.fromisoformat(line[3]).replace(tzinfo=None),
            ))

        if len(line) > 7:
            test = script.setdefault('tests', {})
            test[line[1]] = dict(
                info=int(line[4]),
                success=int(line[5]),
                warning=int(line[6]),
                failure=int(line[7]),
            )
    return parsed


agent_section_netbox_script = AgentSection(
    name = "netbox_script",
    parse_function = parse_netbox_script,
)


def discovery_netbox_script(section):
    for name in section:
        yield Service(item=name)


def check_netbox_script(item, params, section):
    if item not in section:
        return

    script = section[item]

    now = datetime.now()
    if 'last_run' not in script:
        yield Result(state=State.UNKNOWN, summary=(f"Report \"{item}\" not yet executed"))
    else:
        age = now - script['last_run']
        yield from check_levels(
            value=age.total_seconds(),
            levels_upper=params.get('maxage', None),
            render_func=lambda f: render.timespan(f if f > 0 else -f),
            label='Last Run' if age.total_seconds() > 0 else "Last Run in",
        )

    if 'tests' in script:
        info = success = warning = failure = 0
        for test_name, test_result in script['tests'].items():
            info += test_result['info']
            success += test_result['success']
            warning += test_result['warning']
            failure += test_result['failure']

            if test_result['warning'] > 0:
                yield Result(state = State.WARN,
                             summary = f"{test_name} Warning: {test_result['warning']}")

            if test_result['failure'] > 0:
                yield Result(state = State.WARN,
                             summary = f"{test_name} Failure: {test_result['failure']}")

        yield Metric('test_info', info)
        yield Metric('test_success', success)
        yield Metric('test_warning', warning)
        yield Metric('test_failure', failure)


check_plugin_netbox_script = CheckPlugin(
    name = 'netbox_script',
    service_name = 'Netbox Script %s',
    discovery_function = discovery_netbox_script,
    check_function = check_netbox_script,
    check_ruleset_name = 'netbox_script',
    check_default_parameters = {'maxage': ('fixed', (2 * 24 * 3600, 7 * 24 * 3600))},
)
