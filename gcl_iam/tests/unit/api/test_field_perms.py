# Copyright 2026 Genesis Corporation.
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

import contextlib
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import webob
from restalchemy.api import constants
from restalchemy.api import contexts as ra_contexts
from restalchemy.api import packers
from restalchemy.api import resources
from restalchemy.dm import models as ra_models
from restalchemy.dm import properties as ra_properties
from restalchemy.dm import types as ra_types

from gcl_iam import enforcers
from gcl_iam import rules
from gcl_iam.api.field_perms import FieldsIamPermissions
from gcl_iam.api.field_perms import Permissions

RULE = rules.Rule("iam", "custom_props", "list")


def request_for(method=constants.GET):
    req = webob.Request.blank("/things/")
    req.api_context = ra_contexts.RequestContext(req)
    req.api_context.set_active_method(method)
    return req


@contextlib.contextmanager
def enforcing(*perms):
    """A context whose enforcer grants exactly `perms`."""
    context = Mock()
    context.iam_context.enforcer = enforcers.Enforcer(list(perms))
    with patch("gcl_iam.api.field_perms.contexts.get_context") as get_context:
        get_context.return_value = context
        yield context.iam_context.enforcer


def test_init_with_rule_permissions():
    fields = {"field1": {constants.ALL: RULE}}

    permissions = FieldsIamPermissions(fields=fields)

    assert permissions.fields == fields


def test_init_invalid_method():
    with pytest.raises(ValueError):
        FieldsIamPermissions(fields={"field1": {"INVALID_METHOD": Permissions.HIDDEN}})


def test_init_invalid_permission():
    with pytest.raises(ValueError):
        FieldsIamPermissions(fields={"field1": {constants.GET: "INVALID"}})


def test_a_method_gets_the_permission_named_for_it():
    permissions = FieldsIamPermissions(
        fields={
            "field1": {
                constants.GET: Permissions.HIDDEN,
                constants.CREATE: Permissions.RO,
            }
        }
    )

    with enforcing():
        assert permissions.resolve(request_for(constants.GET), ["field1"]) == {
            "field1": Permissions.HIDDEN
        }
        assert permissions.resolve(request_for(constants.CREATE), ["field1"]) == {
            "field1": Permissions.RO
        }


def test_a_field_nobody_named_gets_the_default():
    permissions = FieldsIamPermissions(
        fields={"field1": {constants.CREATE: Permissions.RO}},
        default=Permissions.HIDDEN,
    )

    with enforcing():
        assert permissions.resolve(request_for(), ["field2"]) == {
            "field2": Permissions.HIDDEN
        }


def test_a_rule_the_enforcer_grants_reads_and_writes():
    permissions = FieldsIamPermissions(fields={"field1": {constants.ALL: RULE}})

    with enforcing("iam.custom_props.list"):
        assert permissions.resolve(request_for(), ["field1"]) == {
            "field1": Permissions.RW
        }


def test_a_rule_the_enforcer_denies_hides():
    permissions = FieldsIamPermissions(fields={"field1": {constants.ALL: RULE}})

    with enforcing("iam.something.else"):
        assert permissions.resolve(request_for(), ["field1"]) == {
            "field1": Permissions.HIDDEN
        }


def test_a_rule_standing_as_the_default_answers_for_every_field():
    permissions = FieldsIamPermissions(fields={}, default=RULE)

    with enforcing("iam.something.else"):
        assert permissions.resolve(request_for(), ["field1", "field2"]) == {
            "field1": Permissions.HIDDEN,
            "field2": Permissions.HIDDEN,
        }


def test_each_rule_is_enforced_once_however_many_fields_name_it():
    permissions = FieldsIamPermissions(
        fields={
            "field1": {constants.ALL: RULE},
            "field2": {constants.ALL: RULE},
            "field3": {constants.ALL: rules.Rule("iam", "custom_props", "read")},
        }
    )
    enforcer = Mock()
    enforcer.enforce.return_value = True
    context = Mock()
    context.iam_context.enforcer = enforcer

    with patch("gcl_iam.api.field_perms.contexts.get_context") as get_context:
        get_context.return_value = context
        permissions.resolve(request_for(), ["field1", "field2", "field3"])

    assert enforcer.enforce.call_count == 2


def test_one_field_is_answered_the_same_way_as_all_of_them():
    permissions = FieldsIamPermissions(fields={"field1": {constants.ALL: RULE}})

    with enforcing("iam.something.else"):
        assert permissions.permission_of("field1", request_for()) == Permissions.HIDDEN


class Thing(ra_models.ModelWithUUID):
    name = ra_properties.property(ra_types.String(), default="n")
    custom_props = ra_properties.property(ra_types.String(), default="p")


class TestWhatTheResolutionGuards:
    """The fields two callers are shown, now that a resolution is reused.

    RESTAlchemy keeps a resolved set of fields by what this container
    answered, so these drive it through the packer rather than asking the
    container directly: the requests that must not be told the same.
    """

    def _resource(self, fields=None, default=Permissions.RW):
        return resources.ResourceByRAModel(
            Thing,
            fields_permissions=FieldsIamPermissions(
                default=default,
                fields={"custom_props": {constants.ALL: RULE}}
                if fields is None
                else fields,
            ),
        )

    def _packed(self, resource, method=constants.FILTER):
        packer = packers.BaseResourcePacker(resource, request_for(method))
        return sorted(name for name, _, _ in packer._get_visible_fields())

    def teardown_method(self):
        resources.ResourceMap.model_type_to_resource = {}

    def test_a_caller_without_the_rule_is_not_shown_the_field(self):
        resource = self._resource()

        with enforcing("iam.custom_props.list"):
            assert "custom_props" in self._packed(resource)
        with enforcing("iam.something.else"):
            assert "custom_props" not in self._packed(resource)

    def test_and_not_in_the_other_order_either(self):
        resource = self._resource()

        with enforcing("iam.something.else"):
            assert "custom_props" not in self._packed(resource)
        with enforcing("iam.custom_props.list"):
            assert "custom_props" in self._packed(resource)

    def test_the_two_are_kept_apart_rather_than_not_kept(self):
        # Without this the tests above could pass because nothing is
        # reused at all.
        resource = self._resource()

        with enforcing("iam.custom_props.list"):
            self._packed(resource)
            self._packed(resource)
        with enforcing("iam.something.else"):
            self._packed(resource)

        assert len(resource._visibility_caches) == 2

    def test_a_rule_standing_as_the_default_is_part_of_it_too(self):
        resource = self._resource(fields={}, default=RULE)

        with enforcing("iam.custom_props.list"):
            assert "custom_props" in self._packed(resource)
        with enforcing("iam.something.else"):
            assert "custom_props" not in self._packed(resource)

    def test_a_method_is_told_apart_where_a_rule_is_what_decides(self):
        resource = self._resource(fields={"custom_props": {constants.FILTER: RULE}})

        with enforcing("iam.something.else"):
            assert "custom_props" not in self._packed(resource, constants.FILTER)
            assert "custom_props" in self._packed(resource, constants.GET)

    def test_and_not_in_the_other_order_either_across_methods(self):
        resource = self._resource(fields={"custom_props": {constants.FILTER: RULE}})

        with enforcing("iam.something.else"):
            assert "custom_props" in self._packed(resource, constants.GET)
            assert "custom_props" not in self._packed(resource, constants.FILTER)
