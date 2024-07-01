#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_netbox - Checkmk extension for netbox
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

import pytest  # type: ignore[import]
import datetime
from freezegun import freeze_time
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import netbox_script


SAMPLE_STRING_TABLE = [
    ["DeviceConnectionsReport", "", "completed", "2024-07-01T06:00:02.842382+02:00"],
    ["DeviceConnectionsReport", "test_power_connections", "completed", "2024-07-01T06:00:02.842382+02:00", "0", "76", "0", "0"],
]

SAMPLE_SECTION = {
    'DeviceConnectionsReport': {
        'last_run': datetime.datetime(2024, 7, 1, 6, 0, 2, 842382),
        'name': 'DeviceConnectionsReport',
        'state': 'completed',
        'tests': {
            'test_power_connections': {'failure': 0, 'info': 0, 'success': 76, 'warning': 0},
        },
    },
}


@pytest.mark.parametrize('string_table, result', [
    ([], {}),
    (
        SAMPLE_STRING_TABLE,
        SAMPLE_SECTION
    ),
])
def test_parse_netbox_script(string_table, result):
    assert netbox_script.parse_netbox_script(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (SAMPLE_SECTION, [Service(item='DeviceConnectionsReport')]),
])
def test_discovery_netbox_script(section, result):
    assert list(netbox_script.discovery_netbox_script(section)) == result


@freeze_time('2024-07-02 06:55')
@pytest.mark.parametrize('section, params, result', [
    (SAMPLE_SECTION, {}, [
        Result(state=State.OK, summary='Last Run: 1 day 0 hours'),
        Metric('test_info', 0.0),
        Metric('test_success', 76.0),
        Metric('test_warning', 0.0),
        Metric('test_failure', 0.0),
    ]),
    (SAMPLE_SECTION, {'maxage': ('fixed', (2 * 3600, 7 * 3600))}, [
        Result(state=State.CRIT, summary='Last Run: 1 day 0 hours (warn/crit at 2 hours 0 minutes/7 hours 0 minutes)'),
        Metric('test_info', 0.0),
        Metric('test_success', 76.0),
        Metric('test_warning', 0.0),
        Metric('test_failure', 0.0),
    ]),
])
def test_check_netbox_script(section, params, result):
    assert list(netbox_script.check_netbox_script('DeviceConnectionsReport', params, section)) == result
