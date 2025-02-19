# vim:ts=4:sw=4:et:
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# no unicode literals
from __future__ import absolute_import, division, print_function

import pywatchman
import pywatchman.capabilities
import WatchmanTestCase


@WatchmanTestCase.expand_matrix
class TestCapabilities(WatchmanTestCase.WatchmanTestCase):
    def test_capabilities(self):
        client = self.getClient()
        res = client.query("version")
        self.assertFalse("error" in res, "version with no args still works")

        res = client.query("version", {"optional": ["term-match", "will-never-exist"]})
        self.assertDictEqual(
            res["capabilities"], {"term-match": True, "will-never-exist": False}
        )

        res = client.query(
            "version", {"required": ["term-match"], "optional": ["will-never-exist"]}
        )
        self.assertDictEqual(
            res["capabilities"], {"term-match": True, "will-never-exist": False}
        )
        self.assertFalse("error" in res, "no error for missing optional")

        with self.assertRaisesRegex(
            pywatchman.CommandError,
            "client required capability `will-never-exist` is not "
            + "supported by this server",
        ):
            client.query("version", {"required": ["term-match", "will-never-exist"]})

    def test_capabilityCheck(self):
        client = self.getClient()

        res = client.capabilityCheck(optional=["term-match", "will-never-exist"])
        self.assertDictEqual(
            res["capabilities"], {"term-match": True, "will-never-exist": False}
        )

        res = client.capabilityCheck(
            required=["term-match"], optional=["will-never-exist"]
        )
        self.assertDictEqual(
            res["capabilities"], {"term-match": True, "will-never-exist": False}
        )

        with self.assertRaisesRegex(
            pywatchman.CommandError,
            "client required capability `will-never-exist` is not "
            + "supported by this server",
        ):
            client.capabilityCheck(required=["term-match", "will-never-exist"])

    def test_capabilitySynth(self):
        res = pywatchman.capabilities.synthesize(
            {"version": "1.0"}, {"optional": ["will-never-exist"], "required": []}
        )
        self.assertDictEqual(
            res, {"version": "1.0", "capabilities": {"will-never-exist": False}}
        )

        res = pywatchman.capabilities.synthesize(
            {"version": "1.0"}, {"required": ["will-never-exist"], "optional": []}
        )
        self.assertDictEqual(
            res,
            {
                "version": "1.0",
                "error": "client required capability `will-never-exist` "
                + "is not supported by this server",
                "capabilities": {"will-never-exist": False},
            },
        )

        res = pywatchman.capabilities.synthesize(
            {"version": "3.2"}, {"optional": ["relative_root"], "required": []}
        )
        self.assertDictEqual(
            res, {"version": "3.2", "capabilities": {"relative_root": False}}
        )
        res = pywatchman.capabilities.synthesize(
            {"version": "3.3"}, {"optional": ["relative_root"], "required": []}
        )
        self.assertDictEqual(
            res, {"version": "3.3", "capabilities": {"relative_root": True}}
        )
