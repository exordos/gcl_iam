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
from restalchemy.api import resources


class ProjectResourceByRAModel(resources.ResourceByRAModel):
    """Resource of a model a project-aware controller creates.

    `PolicyBasedController` and `NestedPolicyBasedController` take
    `project_id` from the token (or the parent) when a create body leaves
    it out, so the create schema must not demand it.
    """

    def generate_schema_object(self, method, openapi_version):
        spec = super().generate_schema_object(method, openapi_version)
        if method != constants.CREATE:
            return spec

        project_id = self.get_resource_field_name("project_id")
        required = [name for name in spec.get("required", []) if name != project_id]
        if required:
            spec["required"] = required
        else:
            spec.pop("required", None)
        return spec
