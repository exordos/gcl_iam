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

import pytest
import webob

from gcl_iam import middlewares


def get_otp_code(headers):
    middleware = middlewares.GenesisCoreAuthMiddleware.__new__(
        middlewares.GenesisCoreAuthMiddleware,
    )
    return middleware._get_otp_code(webob.Request.blank("/", headers=headers))


class TestGetOtpCode:
    def test_no_header_means_no_code(self):
        assert get_otp_code({}) is None

    def test_code_is_taken_as_sent(self):
        assert get_otp_code({"X-OTP": "123456"}) == "123456"

    @pytest.mark.parametrize("code", ["012345", "000000"])
    def test_a_leading_zero_survives(self, code):
        # int() would have made these "12345" and 0 -- one unusable, the
        # other indistinguishable from no code at all.
        assert get_otp_code({"X-OTP": code}) == code

    def test_surrounding_whitespace_is_dropped(self):
        assert get_otp_code({"X-OTP": " 123456 "}) == "123456"

    def test_an_empty_header_means_no_code(self):
        assert get_otp_code({"X-OTP": "  "}) is None
