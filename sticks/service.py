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

import os
import socket
import sys

from oslo.config import cfg
from stevedore import named

from sticks.openstack.common import log as logging
from sticks import utils


LOG = logging.getLogger(__name__)

service_opts = [
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help='Name of this node. This can be an opaque identifier. '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within '
               'an AMQP key, and if using ZeroMQ, a valid '
               'hostname, FQDN, or IP address.'),
    cfg.MultiStrOpt('dispatcher',
                    deprecated_group="collector",
                    default=['database'],
                    help='Dispatcher to process data.'),
    cfg.IntOpt('collector_workers',
               default=1,
               help='Number of workers for collector service. A single '
               'collector is enabled by default.'),
    cfg.IntOpt('notification_workers',
               default=1,
               help='Number of workers for notification service. A single '
               'notification agent is enabled by default.'),

]

cfg.CONF.register_opts(service_opts)

CLI_OPTIONS = [
    cfg.StrOpt('os-username',
               deprecated_group="DEFAULT",
               default=os.environ.get('OS_USERNAME', 'sticks'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('os-password',
               deprecated_group="DEFAULT",
               secret=True,
               default=os.environ.get('OS_PASSWORD', 'admin'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('os-tenant-id',
               deprecated_group="DEFAULT",
               default=os.environ.get('OS_TENANT_ID', ''),
               help='Tenant ID to use for OpenStack service access.'),
    cfg.StrOpt('os-tenant-name',
               deprecated_group="DEFAULT",
               default=os.environ.get('OS_TENANT_NAME', 'admin'),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('os-cacert',
               default=os.environ.get('OS_CACERT'),
               help='Certificate chain for SSL validation.'),
    cfg.StrOpt('os-auth-url',
               deprecated_group="DEFAULT",
               default=os.environ.get('OS_AUTH_URL',
                                      'http://localhost:5000/v2.0'),
               help='Auth URL to use for OpenStack service access.'),
    cfg.StrOpt('os-region-name',
               deprecated_group="DEFAULT",
               default=os.environ.get('OS_REGION_NAME'),
               help='Region name to use for OpenStack service endpoints.'),
    cfg.StrOpt('os-endpoint-type',
               default=os.environ.get('OS_ENDPOINT_TYPE', 'publicURL'),
               help='Type of endpoint in Identity service catalog to use for '
                    'communication with OpenStack services.'),
    cfg.BoolOpt('insecure',
                default=False,
                help='Disables X.509 certificate validation when an '
                     'SSL connection to Identity Service is established.'),
]
cfg.CONF.register_opts(CLI_OPTIONS, group="service_credentials")


class WorkerException(Exception):
    """Exception for errors relating to service workers
    """


class DispatchedService(object):

    DISPATCHER_NAMESPACE = 'sticks.dispatcher'

    def start(self):
        super(DispatchedService, self).start()
        LOG.debug(_('loading dispatchers from %s'),
                  self.DISPATCHER_NAMESPACE)
        self.dispatcher_manager = named.NamedExtensionManager(
            namespace=self.DISPATCHER_NAMESPACE,
            names=cfg.CONF.dispatcher,
            invoke_on_load=True,
            invoke_args=[cfg.CONF])
        if not list(self.dispatcher_manager):
            LOG.warning(_('Failed to load any dispatchers for %s'),
                        self.DISPATCHER_NAMESPACE)


def get_workers(name):
    workers = (cfg.CONF.get('%s_workers' % name) or
               utils.cpu_count())
    if workers and workers < 1:
        msg = (_("%(worker_name)s value of %(workers)s is invalid, "
                 "must be greater than 0") %
               {'worker_name': '%s_workers' % name, 'workers': str(workers)})
        raise WorkerException(msg)
    return workers


def prepare_service(argv=None):
    cfg.set_defaults(logging.log_opts,
                     default_log_levels=['amqplib=WARN',
                                         'qpid.messaging=INFO',
                                         'sqlalchemy=WARN',
                                         'keystoneclient=INFO',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=WARN',
                                         'iso8601=WARN'
                                         ])
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='sticks')
    logging.setup('sticks')
