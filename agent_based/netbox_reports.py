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

# <<<netbox_reports>>>
# dellos6.DellOS6Report,DellOS6Report,test_device
# dellos6.DellOS6Report,DellOS6Report,test_interface
# devices.DeviceConnectionsReport,DeviceConnectionsReport,test_power_connections
# dhcp.DhcpReport,DhcpReport,test_pool_is_in_prefix,2023-01-04T08:00:01.134531+01:00,0,0,41,0
# dhcp.DhcpReport,DhcpReport,test_prefix_has_pool,2023-01-04T08:00:01.134531+01:00,0,0,41,0
# ipam.IpAddressReport,IpAddressReport,test_name_or_description,2022-12-22T14:20:32.555035+01:00,0,23,0,0
# ipam.PrefixReport,PrefixReport,test_broadcast_reservation,2022-12-21T16:01:17.599839+01:00,0,0,101,0
# ipam.PrefixReport,PrefixReport,test_no_subprefix_in_active,2022-12-21T16:01:17.599839+01:00,0,1,100,0

from .agent_based_api.v1 import (
    check_levels,
    Metric,
    register,
    render,
    Result,
    Service,
    State,
)

from datetime import datetime

def parse_netbox_reports(string_table):
    parsed = {}

    for line in string_table:
        if line[0] not in parsed:
            parsed[line[0]] = {}

        parsed[line[0]][line[2]] = {}

        if len(line) == 3:
            continue

        last_run_dt = datetime.fromisoformat(line[3]).replace(tzinfo=None)

        parsed[line[0]]['last_run'] = last_run_dt
        parsed[line[0]][line[2]]['result'] = {
            'info': int(line[4]),
            'success': int(line[5]),
            'warning': int(line[6]),
            'failure': int(line[7]),
        }

    # print (parsed)
    return parsed

register.agent_section(
    name = "netbox_reports",
    parse_function = parse_netbox_reports,
)

def discover_netbox_reports(section):
    for name in section:
        yield Service(item=name)

def check_netbox_reports(item, params, section):

    report = section[item]

    now = datetime.now()
    if not 'last_run' in report:
        yield Result(state=State.UNKNOWN, summary=(f"Report \"{item}\" not yet executed"))
    else:
        age = now - report['last_run']
        yield from check_levels(
                value=age.total_seconds(),
                levels_upper=params.get('maxage', None),
                render_func=lambda f: render.timespan(f if f > 0 else -f),
                label='Last Run' if age.total_seconds() > 0 else "Last Run in",
            )

        for test_name in report:
            if test_name == 'last_run':
                continue

            yield Result(state = State.OK, summary = f"{test_name}",
                                           details = f"{test_name}: {report[test_name]['result']}")

            if report[test_name]['result']['warning'] > 0:
                yield Result (state = State.WARN,
                              summary = f"Warning: {report[test_name]['result']['warning']}")

            if report[test_name]['result']['failure'] > 0:
                yield Result (state = State.WARN,
                         summary = f"Failure: {report[test_name]['result']['failure']}")

            for key, value in report[test_name]['result'].items():
                yield Metric (f"{test_name}_{key}", value)

register.check_plugin(
    name = "netbox_reports",
    service_name = "Netbox Reports %s",
    discovery_function = discover_netbox_reports,
    check_function = check_netbox_reports,
    check_ruleset_name = "netbox_reports",
    check_default_parameters = {'maxage': (2*24*3600, 7*24*3600)},
)