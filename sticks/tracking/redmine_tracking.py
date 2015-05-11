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

from oslo.config import cfg
import redmine

from sticks.api.v1.datamodels import ticket as ticket_models
from sticks.openstack.common import log
from sticks import tracking

LOG = log.getLogger(__name__)

redmine_group = cfg.OptGroup(name='redmine', title='Redmine plugin options')

redmine_group_opts = [
    cfg.StrOpt('redmine_url', help='Redmine server URL', default='http://'),
    cfg.StrOpt('redmine_login', help='Redmine API user', default=''),
    cfg.StrOpt('redmine_password', help='Redmine API password', default=''),
]
cfg.CONF.register_group(redmine_group)
cfg.CONF.register_opts(redmine_group_opts, group=redmine_group)


OPTS = [
    cfg.StrOpt('tracking_plugin', default='redmine'),
]


class RedmineTracking(tracking.TrackingBase):
    """Redmine tracking driver."""

    mapping_ticket = dict(
        title='subject',
        project='project_id',
    )

    def __init__(self):
        super(RedmineTracking, self).__init__()
        super(RedmineTracking, self).subscribe_event(
            self._ROLE_ASSIGNMENT_CREATED)
        self.redmine = redmine.Redmine(cfg.CONF.redmine.redmine_url,
                                       username=cfg.CONF.
                                       redmine.redmine_login,
                                       password=cfg.CONF.
                                       redmine.redmine_password)

    def _from_issue(self, issue):
        """Create a TicketResource from redmine Issue

        :param issue: Redmine issue object
        :return: TicketResource
        """
        return ticket_models.TicketResource(id=str(issue.id),
                                            title=issue.subject,
                                            status=issue.status.name,
                                            start_date=issue.start_date,
                                            project=issue.project.name
                                            )

    def _to_resource(self, dic, mapping):
        """Make mapping betweeb dict representation of  Resource Type
        and redmine resource representation

        :param dic: dict representation of Resource (datamodels)
        :param mapping: mapping

        :return: json
        """
        return {mapping[k]: v for k, v in dic.items()}

    def _redmine_create(self, data):
        return self.redmine.issue.create(**data)

    def _get_issues(self, project_id):
        project = self.redmine.project.get(project_id)
        return project.issues

    def create_ticket(self, data):
        """Create an issue

        :param data: TicketResource
        :return: TicketResource of created ticket
        """
        resp = self._redmine_create(self._to_resource(
                                    data.as_dict(),
                                    self.mapping_ticket))

        return self._from_issue(resp)

    def get_tickets(self, project_id):
        """Return all issues filtered by project_id

        :param project_id:
        :return: TicketResourceCollection
        """
        issues = self._get_issues(project_id)

        return ticket_models.TicketResourceCollection(
            tickets=[self._from_issue(issue) for issue in issues])

    def get_ticket(self, ticket_id):
        """Return issue with given id

        :param ticket_id:
        :return: TicketResource
        """
        issue = self.redmine.issue.get(ticket_id)

        return self._from_issue(issue)

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        """Specific notification processing."""
        super(RedmineTracking, self).process_notification(ctxt,
                                                          publisher_id,
                                                          event_type, payload,
                                                          metadata)

    def create_project(self, identifier, project_name):
        """Create a tracking project

        :param data: ProjectResource
        :return: ProjectResource of created project
        """
        resp = self.redmine.project.create(project=identifier,
                                           name=project_name,
                                           identifier=identifier)

        return resp
