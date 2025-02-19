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

import json
import os

import WatchmanInstance
import WatchmanTestCase


@WatchmanTestCase.expand_matrix
class TestInfo(WatchmanTestCase.WatchmanTestCase):
    def test_sock_name(self):
        resp = self.watchmanCommand("get-sockname")
        self.assertEqual(
            resp["sockname"],
            WatchmanInstance.getSharedInstance().getSockPath().legacy_sockpath(),
        )

    def test_get_config_empty(self):
        root = self.mkdtemp()
        self.watchmanCommand("watch", root)
        resp = self.watchmanCommand("get-config", root)
        self.assertEqual(resp["config"], {})

    def test_get_config(self):
        config = {"test-key": "test-value"}
        root = self.mkdtemp()
        with open(os.path.join(root, ".watchmanconfig"), "w") as f:
            json.dump(config, f)
        self.watchmanCommand("watch", root)
        resp = self.watchmanCommand("get-config", root)
        self.assertEqual(resp["config"], config)
