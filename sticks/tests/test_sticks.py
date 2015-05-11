#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
"""
test_sticks
----------------------------------

Tests for `sticks` module.
"""
from stevedore import driver

from sticks.tests import base
from sticks.tracking import redmine_tracking


class TestSticks(base.TestBase):

    def test_call(self):
        def invoke(ext, *args, **kwds):
            return (ext.name, args, kwds)
        dm = driver.DriverManager('sticks.tracking', 'redmine',
                                  invoke_on_load=True,)
        self.assertIsInstance(dm.driver, redmine_tracking.RedmineTracking)
