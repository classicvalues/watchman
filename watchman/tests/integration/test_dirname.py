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

import os

import WatchmanTestCase


@WatchmanTestCase.expand_matrix
class TestDirName(WatchmanTestCase.WatchmanTestCase):
    def test_dirname(self):
        root = self.mkdtemp()
        for i in range(0, 5):
            istr = str(i)
            os.makedirs(os.path.join(root, istr, istr, istr, istr, istr))
            self.touchRelative(root, "a")
            self.touchRelative(root, istr, "a")
            self.touchRelative(root, "%sa" % istr)
            self.touchRelative(root, istr, istr, "a")
            self.touchRelative(root, istr, istr, istr, "a")
            self.touchRelative(root, istr, istr, istr, istr, "a")
            self.touchRelative(root, istr, istr, istr, istr, istr, "a")

        self.watchmanCommand("watch", root)

        tests = [
            [
                "",
                None,
                [
                    "0/0/0/0/0/a",
                    "0/0/0/0/a",
                    "0/0/0/a",
                    "0/0/a",
                    "0/a",
                    "1/1/1/1/1/a",
                    "1/1/1/1/a",
                    "1/1/1/a",
                    "1/1/a",
                    "1/a",
                    "2/2/2/2/2/a",
                    "2/2/2/2/a",
                    "2/2/2/a",
                    "2/2/a",
                    "2/a",
                    "3/3/3/3/3/a",
                    "3/3/3/3/a",
                    "3/3/3/a",
                    "3/3/a",
                    "3/a",
                    "4/4/4/4/4/a",
                    "4/4/4/4/a",
                    "4/4/4/a",
                    "4/4/a",
                    "4/a",
                    "a",
                ],
            ],
            [
                "",
                4,
                [
                    "0/0/0/0/0/a",
                    "1/1/1/1/1/a",
                    "2/2/2/2/2/a",
                    "3/3/3/3/3/a",
                    "4/4/4/4/4/a",
                ],
            ],
            [
                "",
                3,
                [
                    "0/0/0/0/0/a",
                    "0/0/0/0/a",
                    "1/1/1/1/1/a",
                    "1/1/1/1/a",
                    "2/2/2/2/2/a",
                    "2/2/2/2/a",
                    "3/3/3/3/3/a",
                    "3/3/3/3/a",
                    "4/4/4/4/4/a",
                    "4/4/4/4/a",
                ],
            ],
            ["0", None, ["0/0/0/0/0/a", "0/0/0/0/a", "0/0/0/a", "0/0/a", "0/a"]],
            ["1", None, ["1/1/1/1/1/a", "1/1/1/1/a", "1/1/1/a", "1/1/a", "1/a"]],
            ["1", 0, ["1/1/1/1/1/a", "1/1/1/1/a", "1/1/1/a", "1/1/a"]],
            ["1", 1, ["1/1/1/1/1/a", "1/1/1/1/a", "1/1/1/a"]],
            ["1", 2, ["1/1/1/1/1/a", "1/1/1/1/a"]],
            ["1", 3, ["1/1/1/1/1/a"]],
            ["1", 4, []],
        ]

        for (dirname, depth, expect) in tests:
            if depth is None:
                # equivalent to `depth ge 0`
                term = ["dirname", dirname]
            else:
                term = ["dirname", dirname, ["depth", "gt", depth]]

            label = repr([dirname, depth, expect, term])

            results = self.watchmanCommand(
                "query",
                root,
                {"expression": ["allof", term, ["name", "a"]], "fields": ["name"]},
            )

            self.assertFileListsEqual(results["files"], expect, label)
