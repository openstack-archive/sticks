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
import pecan
from pecan import core
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from sticks.api.v1.datamodels import ticket as ticket_models
from sticks import manager
from sticks.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class TicketsController(rest.RestController):
    """REST Controller ticket management."""

    def __init__(self):
        self.sticks_manager = manager.SticksManager()

    @wsme_pecan.wsexpose(ticket_models.TicketResourceCollection,
                         wtypes.text)
    def get_all(self, project):
        """Return all tickets"""
        return self.sticks_manager.dm.driver.get_tickets(project)

    @wsme_pecan.wsexpose(ticket_models.TicketResource,
                         wtypes.text)
    def get(self, ticket_id):
        """Return ticket"""
        return self.sticks_manager.dm.driver.get_ticket(ticket_id)

    @wsme_pecan.wsexpose(ticket_models.TicketResource,
                         body=ticket_models.TicketResource)
    def post(self, data):
        """Create a ticket"""
        return self.sticks_manager.dm.driver.create_ticket(data)

    @pecan.expose()
    def put(self):
        core.response.status = 204
        return

    @pecan.expose()
    def delete(self):
        core.response.status = 200
        return
