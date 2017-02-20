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


import abc
import fnmatch
import six

from oslo.config import cfg
from oslo import messaging

from sticks.client import keystone_client
from sticks.openstack.common.gettextutils import _  # noqa


sticks_role_opt = [
    cfg.StrOpt('sticks_role_name', default='sticks',
               help=_('Required role to issue tickets.'))
]

CONF = cfg.CONF
CONF.register_opts(sticks_role_opt)


@six.add_metaclass(abc.ABCMeta)
class TrackingBase(object):
    """Base class for tracking plugin."""

    _name = None

    _ROLE_ASSIGNMENT_CREATED = 'identity.created.role_assignment'

    def __init__(self, description=None, provider=None, type=None,
                 tool_name=None):
        self.default_events = [self._ROLE_ASSIGNMENT_CREATED]
        self._subscribedEvents = self.default_events
        self._name = "{0}.{1}".format(self.__class__.__module__,
                                      self.__class__.__name__)
        self.kc = None
        self.conf = CONF

    def subscribe_event(self, event):
        if not (event in self._subscribedEvents):
            self._subscribedEvents.append(event)

    def register_manager(self, manager):
        """
        Enables the plugin to add tasks to the  manager
        :param manager: the task manager to add tasks to
        """
        self.manager = manager

    def _has_sticks_role(self, user_id, role_id, project_id):
        """
        Evaluates whether this user has sticks role. Returns
        ``True`` or ``False``.
        """
        if self.kc is None:
            self.kc = keystone_client.Client()

        roles = [role.name for role in
                 self.kc.roles_for_user(user_id, project_id)
                 if role.id == role_id]
        return self.conf.sticks_role_name in [role.lower() for role in roles]

    @abc.abstractmethod
    def create_ticket(self, data):
        """Create a ticket with data.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """

    @abc.abstractmethod
    def create_project(self, data):
        """Create a tracking project.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """

    @staticmethod
    def _handle_event_type(subscribed_events, event_type):
        """Check whether event_type should be handled.

        It is according to event_type_to_handle.l
        """
        return any(map(lambda e: fnmatch.fnmatch(event_type, e),
                       subscribed_events))

    @staticmethod
    def get_targets(conf):
        """Return a sequence of oslo.messaging.Target

        Sequence defining the exchange and topics to be connected for this
        plugin.
        """
        return [messaging.Target(topic=topic)
                for topic in cfg.CONF.notification_topics]

    def get_project(self, project_id):

        if self.kc is None:
            self.kc = keystone_client.Client()

        return self.kc.project_get(project_id)

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        """ Process events"""
        # Default action : create project
        if event_type == self._ROLE_ASSIGNMENT_CREATED:
            project = self.get_project(payload['project'])
            if self._has_sticks_role(payload['user'],
                                     payload['role'],
                                     payload['project']):
                self.create_project(payload['project'], project.name)

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        # Check if event is registered for plugin
        if self._handle_event_type(self._subscribedEvents, event_type):
            self.process_notification(ctxt, publisher_id, event_type, payload,
                                      metadata)
