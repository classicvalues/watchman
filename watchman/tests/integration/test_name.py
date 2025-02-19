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

import pywatchman
import WatchmanTestCase


@WatchmanTestCase.expand_matrix
class TestNameExpr(WatchmanTestCase.WatchmanTestCase):
    def test_name_expr(self):
        root = self.mkdtemp()

        self.touchRelative(root, "foo.c")
        os.mkdir(os.path.join(root, "subdir"))
        self.touchRelative(root, "subdir", "bar.txt")

        self.watchmanCommand("watch", root)

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query", root, {"expression": ["iname", "FOO.c"], "fields": ["name"]}
            )["files"],
            ["foo.c"],
        )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {"expression": ["iname", ["FOO.c", "INVALID.txt"]], "fields": ["name"]},
            )["files"],
            ["foo.c"],
        )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query", root, {"expression": ["name", "foo.c"], "fields": ["name"]}
            )["files"],
            ["foo.c"],
        )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {"expression": ["name", ["foo.c", "invalid"]], "fields": ["name"]},
            )["files"],
            ["foo.c"],
        )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {"expression": ["name", "foo.c", "wholename"], "fields": ["name"]},
            )["files"],
            ["foo.c"],
        )

        if self.isCaseInsensitive():
            self.assertFileListsEqual(
                self.watchmanCommand(
                    "query",
                    root,
                    {"expression": ["name", "Foo.c", "wholename"], "fields": ["name"]},
                )["files"],
                ["foo.c"],
            )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {"expression": ["name", "bar.txt", "wholename"], "fields": ["name"]},
            )["files"],
            [],
        )

        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {
                    "expression": ["name", "bar.txt", "wholename"],
                    "relative_root": "subdir",
                    "fields": ["name"],
                },
            )["files"],
            ["bar.txt"],
        )

        # foo.c is not in subdir so this shouldn't return any matches
        self.assertFileListsEqual(
            self.watchmanCommand(
                "query",
                root,
                {
                    "expression": ["name", "foo.c", "wholename"],
                    "relative_root": "subdir",
                    "fields": ["name"],
                },
            )["files"],
            [],
        )

        with self.assertRaises(pywatchman.WatchmanError) as ctx:
            self.watchmanCommand("query", root, {"expression": "name"})

        self.assertRegex(str(ctx.exception), "Expected array for 'i?name' term")

        with self.assertRaises(pywatchman.WatchmanError) as ctx:
            self.watchmanCommand(
                "query", root, {"expression": ["name", "one", "two", "three"]}
            )

        self.assertRegex(
            str(ctx.exception), "Invalid number of arguments for 'i?name' term"
        )

        with self.assertRaises(pywatchman.WatchmanError) as ctx:
            self.watchmanCommand("query", root, {"expression": ["name", 2]})

        self.assertRegex(
            str(ctx.exception),
            ("Argument 2 to 'i?name' must be either a string " "or an array of string"),
        )

        with self.assertRaises(pywatchman.WatchmanError) as ctx:
            self.watchmanCommand("query", root, {"expression": ["name", "one", 2]})

        self.assertRegex(str(ctx.exception), "Argument 3 to 'i?name' must be a string")

        with self.assertRaises(pywatchman.WatchmanError) as ctx:
            self.watchmanCommand(
                "query", root, {"expression": ["name", "one", "invalid"]}
            )

        self.assertRegex(
            str(ctx.exception), "Invalid scope 'invalid' for i?name expression"
        )
