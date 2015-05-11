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

import datetime
import json

import mock

from sticks.tests.api import base


class MockResource(object):
    name = None
    id = None

    def __init__(self, name, id):
        self.name = name
        self.id = id


class MockStatus(MockResource):
    pass


class MockProject(MockResource):
    pass


class MockIssue(object):
    subject = None
    id = None
    status = None
    project = None
    start_date = None

    def __init__(self, id, project, subject, status, start_date):
        self.id = id
        self.subject = subject
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        self.status = MockStatus(status, "123")
        self.project = MockProject(project, "123")


class TestTicket(base.TestApiBase):

    def setUp(self):
        super(TestTicket, self).setUp()
        application = self.app.app.application
        self.tracking = application.root.v1.tickets.sticks_manager.dm.driver
        self.tracking.redmine = mock.MagicMock()

    def test_get_all(self):
        response_body = {'tickets': [{'project': 'test_project_1',
                                      'status': 'test_status_1',
                                      'start_date': '2015-01-01T00:00:00',
                                      'id': 'test_id_1',
                                      'title': 'test_subject_1',
                                      },
                                     {'project': 'test_project_2',
                                      'status': 'test_status_2',
                                      'start_date': '2015-01-01T00:00:00',
                                      'id': 'test_id_2',
                                      'title': 'test_subject_2',
                                      }]}
        mock_issues = [MockIssue("test_id_1",
                                 "test_project_1",
                                 "test_subject_1",
                                 "test_status_1",
                                 "2015-01-01"),
                       MockIssue("test_id_2",
                                 "test_project_2",
                                 "test_subject_2",
                                 "test_status_2",
                                 "2015-01-01"),
                       ]

        self.tracking._get_issues = mock.MagicMock(return_value=mock_issues)

        resp = self.app.get('/v1/tickets', {'project': 'foo'})

        self.assertEqual(json.loads(resp.body), response_body)

    def test_get_ticket(self):

        response_body = {'project': 'test_project_1',
                                    'status': 'test_status_1',
                                    'start_date': '2015-01-01T00:00:00',
                                    'id': 'test_id_1',
                                    'title': 'test_subject_1',
                         }
        mock_issue = MockIssue("test_id_1",
                               "test_project_1",
                               "test_subject_1",
                               "test_status_1",
                               "2015-01-01")

        self.tracking.redmine.issue.get = mock.MagicMock(
            return_value=mock_issue)

        resp = self.app.get('/v1/tickets/1', )

        self.assertEqual(json.loads(resp.body), response_body)

    def test_post_ticket(self):
        response_body = {'project': 'test_project_1',
                                    'status': 'test_status_1',
                                    'start_date': '2015-01-01T00:00:00',
                                    'id': 'test_id_1',
                                    'title': 'test_subject_1',
                         }
        mock_issue = MockIssue("test_id_1",
                               "test_project_1",
                               "test_subject_1",
                               "test_status_1",
                               "2015-01-01")

        self.tracking._redmine_create = mock.MagicMock(return_value=mock_issue)

        resp = self.post_json('/tickets', {'project': 'foo', 'title': 'bar'})

        # Check message
        self.assertEqual(json.loads(resp.body), response_body)
