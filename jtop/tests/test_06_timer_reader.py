# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019-2023 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pytest
from ..core import timer_reader


class FakeTime(object):
    """Wall clock that can be stepped, monotonic clock that advances only through sleep()."""

    def __init__(self):
        self.wall = 1700000000.0
        self.mono = 1000.0
        self.sleeps = []

    def time(self):
        return self.wall

    def monotonic(self):
        return self.mono

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.wall += seconds
        self.mono += seconds


@pytest.mark.parametrize("step", [-3600.0, 3600.0])
def test_timer_reader_ignores_wall_clock_step(monkeypatch, step):
    # A wall-clock step during one read must not change the sleep that follows it. On wall time a
    # step back of an hour made the reader sleep for interval + 1 h, stalling the service.
    fake = FakeTime()
    monkeypatch.setattr(timer_reader, "time", fake)
    calls = []

    def callback():
        calls.append(None)
        if len(calls) == 2:
            fake.wall += step
        if len(calls) == 4:
            reader._stop_event.clear()

    reader = timer_reader.TimerReader(callback)
    reader._stop_event.set()
    reader._timer_callback(0.5, reader._stop_event)
    assert fake.sleeps == [0.5, 0.5, 0.5, 0.5]
# EOF
