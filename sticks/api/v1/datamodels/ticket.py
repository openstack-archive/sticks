#
# Copyright (c) 2015 EUROGICIEL
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
#
import datetime

from sticks.api.v1.datamodels import base
from wsme import types as wtypes


class TicketResource(base.Base):
    """Type describing a ticket.

    """

    title = wtypes.text
    """Title of the ticket."""

    id = wtypes.text
    """Id of the ticket."""

    description = wtypes.text
    """Description of the ticket."""

    project = wtypes.text
    """Associated project of the ticket."""

    start_date = datetime.date
    """Start date."""

    status = wtypes.text
    """Status."""

    category = wtypes.text
    """Category ."""

    def as_dict(self):
        return self.as_dict_from_keys(['title', 'id', 'project', 'start_date',
                                       'status', 'description', 'category'])

    @classmethod
    def sample(cls):
        sample = cls(project='test_project',
                     title='Ticket incident')
        return sample


class TicketResourceCollection(base.Base):
    """A list of Tickets."""

    tickets = [TicketResource]
