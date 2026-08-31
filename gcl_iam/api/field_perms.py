#    Copyright 2026 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

from restalchemy.api import constants
from restalchemy.api import field_permissions as field_p
from restalchemy.common import contexts

from gcl_iam import rules

# Make it easier to use
Permissions = field_p.Permissions


class FieldsIamPermissions(field_p.BasePermissions):
    def __init__(self, fields, default=Permissions.RW):
        """Field permissions container for resource

        It's based on FieldsPermissions but with Rules support.

        This class describes a dict of fields with permissions for
        various RestAlchemy API methods. All permissions are declared
        in class Permissions. The methods supported by RA are declared
        in the `restalchemy.api.constants` module.
        For example, the code below shows how to set:
        > HIDDEN permissions to the `one_field` for the FILTER method
          and RW for all others RA methods, except FILTER;
        > RO permissions for the `two_field` for all RA methods;
        > HIDDEN permissions for the `three_field` for GET method and
          RO permissions for all others RA methods, except GET.

        In addition, it supports iam permissions check via gcl_iam enforcer.

        Example:

        ```
        FieldsPermissions(
            default=Permissions.RW,
            fields={
                'one_field':{
                    constants.FILTER: Permissions.HIDDEN},
                'two_field': {
                    constants.ALL: Permissions.RO},
                'three_field': {
                    constants.GET: Permissions.HIDDEN,
                    constants.ALL: Permissions.RO},
                'perm_based_field': {
                    constants.ALL: rules.Rule('service', 'res', 'perm')}
            }
        )
        ```

        Pay attention: if you wouldn't set permission for field and RA method
        by default it would be RW (READWRITE) permission.

        :param fields: dict of field model name and permissions
        :param default: default permission for non-described fields
        """
        for field, method_permission in fields.items():
            for method, permission in method_permission.items():
                if method.upper() not in constants.ALL_RA_METHODS:
                    raise ValueError(
                        "Unknown RA method %r for field %r" % (method, field)
                    )
                if not (
                    permission in Permissions.ALL_PERMISSIONS
                    or isinstance(permission, rules.Rule)
                ):
                    raise ValueError(
                        "Unknown permission %r for field %r" % (permission, field)
                    )
        super().__init__(permission=default)
        self.fields = fields

    @property
    def _enforcer(self):
        return contexts.get_context().iam_context.enforcer

    def resolve(self, req, field_names):
        """What this request may do with each of `field_names`.

        The RA method and the enforcer are read once for the whole
        resource rather than once per field, and a rule is enforced once
        however many fields name it.
        """
        method = req.api_context.get_active_method()
        granted = {}
        return {
            name: self._permission_for(name, method, granted) for name in field_names
        }

    def _permission_for(self, model_field_name, method, granted):
        field_permission = self.fields.get(model_field_name, {})

        # NOTE(g.melikov): By DEFAULT permission is Permissions.RW
        permission = (
            field_permission.get(method)
            or field_permission.get(constants.ALL)
            or self._permission
        )

        if isinstance(permission, rules.Rule):
            allowed = granted.get(permission)
            if allowed is None:
                allowed = bool(self._enforcer.enforce(permission, do_raise=False))
                granted[permission] = allowed
            permission = Permissions.RW if allowed else Permissions.HIDDEN

        return permission
