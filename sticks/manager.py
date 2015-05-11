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
from oslo import messaging

from stevedore import driver

from sticks.openstack.common import log
from sticks.openstack.common import service


LOG = log.getLogger(__name__)

OPTS = [
    cfg.StrOpt('tracking_plugin', default='redmine'),
    cfg.ListOpt('notification_topics', default=['notifications', ],
                help='AMQP topic used for OpenStack notifications'),
    cfg.MultiStrOpt('messaging_urls',
                    default=[],
                    help="Messaging URLs to listen for notifications. "
                         "Example: transport://user:pass@host1:port"
                         "[,hostN:portN]/virtual_host "
                         "(DEFAULT/transport_url is used if empty)"),
]

cfg.CONF.register_opts(OPTS)


class SticksManager(service.Service):

    def __init__(self):
        super(SticksManager, self).__init__()
        self.dm = driver.DriverManager(
            namespace='sticks.tracking',
            name=cfg.CONF.tracking_plugin,
            invoke_on_load=True,
        )

    def start(self):
        self.notification_server = None
        super(SticksManager, self).start()

        targets = []
        plugins = []

        driver = self.dm.driver
        LOG.debug(('Event types from %(name)s: %(type)s')
                  % {'name': driver._name,
                     'type': ', '.join(driver._subscribedEvents)})

        driver.register_manager(self)
        targets.extend(driver.get_targets(cfg.CONF))
        plugins.append(driver)

        transport = messaging.get_transport(cfg.CONF)

        if transport:
            self.notification_server = messaging.get_notification_listener(
                transport, targets, plugins, executor='eventlet')

            self.notification_server.start()
