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
from cmk.agent_based.v2 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import netbox_data_source


SAMPLE_STRING_TABLE = [
    ['{"name": "test", "description": "test", "enabled": true, "status": {"value": "completed", "label": "Completed"}, "last_synced": "2023-05-03T13:13:29.965921+02:00", "file_count": 1}'],
]

SAMPLE_SECTION = {
    "test": {"name": "test", "description": "test", "enabled": True, "status": {"value": "completed", "label": "Completed"}, "last_synced": datetime.datetime(2023, 5, 3, 13, 13, 29, 965921), "file_count": 1}
}


@pytest.mark.parametrize('string_table, result', [
    ([], {}),
    (
        SAMPLE_STRING_TABLE,
        SAMPLE_SECTION
    ),
])
def test_parse_netbox_report(string_table, result):
    assert netbox_data_source.parse_netbox_data_source(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (SAMPLE_SECTION, [Service(item='test')]),
])
def test_discovery_netbox_data_source(section, result):
    assert list(netbox_data_source.discovery_netbox_data_source(section)) == result


@freeze_time('2023-05-04 06:55')
@pytest.mark.parametrize('section, params, result', [
    (SAMPLE_SECTION, {}, [Result(state=State.OK, summary='Last Sync: 17 hours 41 minutes'), Metric('file', 1.0)]),
    (SAMPLE_SECTION, {'maxage': ('fixed', (2 * 3600, 7 * 3600))}, [Result(state=State.CRIT, summary='Last Sync: 17 hours 41 minutes (warn/crit at 2 hours 0 minutes/7 hours 0 minutes)'), Metric('file', 1.0)]),
])
def test_check_netbox_data_source(section, params, result):
    assert list(netbox_data_source.check_netbox_data_source('test', params, section)) == result
