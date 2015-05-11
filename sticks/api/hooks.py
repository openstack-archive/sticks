#
#   Copyright (c) 2015 EUROGICIEL
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
from pecan import hooks
from webob import exc

from sticks.common import context
from sticks.common import policy


class ConfigHook(hooks.PecanHook):
    """Attach the config object to the request so controllers can get to it."""

    def before(self, state):
        state.request.cfg = cfg.CONF


class ContextHook(hooks.PecanHook):
    """Configures a request context and attaches it to the request.

    The following HTTP request headers are used:

    X-User-Id or X-User:
        Used for context.user_id.

    X-Tenant-Id or X-Tenant:
        Used for context.tenant.

    X-Auth-Token:
        Used for context.auth_token.

    X-Roles:
        Used for setting context.is_admin flag to either True or False.
        The flag is set to True, if X-Roles contains either an administrator
        or admin substring. Otherwise it is set to False.

    """
    def __init__(self, public_api_routes):
        self.public_api_routes = public_api_routes
        super(ContextHook, self).__init__()

    def before(self, state):
        user_id = state.request.headers.get('X-User-Id')
        user_id = state.request.headers.get('X-User', user_id)
        tenant_id = state.request.headers.get('X-Tenant-Id')
        tenant = state.request.headers.get('X-Tenant', tenant_id)
        domain_id = state.request.headers.get('X-User-Domain-Id')
        domain_name = state.request.headers.get('X-User-Domain-Name')
        auth_token = state.request.headers.get('X-Auth-Token')
        roles = state.request.headers.get('X-Roles', '').split(',')
        creds = {'roles': roles}

        is_public_api = state.request.environ.get('is_public_api', False)
        is_admin = policy.enforce('context_is_admin',
                                  state.request.headers,
                                  creds)

        state.request.context = context.RequestContext(
            auth_token=auth_token,
            user=user_id,
            tenant_id=tenant_id,
            tenant=tenant,
            domain_id=domain_id,
            domain_name=domain_name,
            is_admin=is_admin,
            is_public_api=is_public_api,
            roles=roles)


class AdminAuthHook(hooks.PecanHook):
    """Verify that the user has admin rights.

    Checks whether the request context is an admin context and
    rejects the request if the api is not public.

    """
    def before(self, state):
        ctx = state.request.context

        if not ctx.is_admin and not ctx.is_public_api:
            raise exc.HTTPForbidden()
