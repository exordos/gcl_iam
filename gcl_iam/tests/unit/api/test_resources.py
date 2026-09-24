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

from restalchemy.api import constants
from restalchemy.dm import models as ra_models
from restalchemy.dm import properties as ra_properties
from restalchemy.dm import types as ra_types

from gcl_iam.api import resources


class Server(ra_models.ModelWithUUID, ra_models.ModelWithProject):
    name = ra_properties.property(ra_types.String(), required=True)


def schema(method, convert_underscore=False):
    resource = resources.ProjectResourceByRAModel(
        Server, convert_underscore=convert_underscore
    )
    return resource.generate_schema_object(method, "3.0.3")


def test_create_does_not_require_project_id():
    create = schema(constants.CREATE)

    assert "project_id" in create["properties"]
    assert create["required"] == ["name"]


def test_create_drops_project_id_under_its_api_name():
    create = schema(constants.CREATE, convert_underscore=True)

    assert "project-id" in create["properties"]
    assert "project-id" not in create["required"]


def test_get_keeps_project_id_required():
    assert "project_id" in schema(constants.GET)["required"]
