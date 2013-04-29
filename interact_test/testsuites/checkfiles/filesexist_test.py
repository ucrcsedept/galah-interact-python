# Copyright (c) 2013 Galah Group LLC
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of galah-interact-python.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright (c) 2013 Galah Group LLC
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of galah-interact-python.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from interact.testsuites.checkfiles.filesexist import *
import interact_test.testcore as testcore
import tempfile
import shutil

import unittest
class TestCheckFilesExist(unittest.TestCase):
    def test_missing_files(self):
        temp_dir = tempfile.mkdtemp()

        try:
            test_files = [
                os.path.join(temp_dir, i) for i in ["hello.txt", "goodbye.txt"]
            ]

            test_result = check_files_exist(*test_files)

            self.assertFalse(test_result.is_passing())

            self.assertEquals(len(test_result.messages), 1)
            self.assertItemsEqual(
                test_result.messages[0].kwargs["missing_files"], test_files
            )
        finally:
            shutil.rmtree(temp_dir)

    def test_extant_files(self):
        temp_dir = tempfile.mkdtemp()

        try:
            test_files = [
                os.path.join(temp_dir, i) for i in ["hello.txt", "goodbye.txt"]
            ]

            for i in test_files:
                with open(i, "w") as f:
                    print >> f, "Hello world!"

            test_result = check_files_exist(*test_files)

            self.assertTrue(test_result.is_passing())

            self.assertListEqual(test_result.messages, [])
        finally:
            shutil.rmtree(temp_dir)
