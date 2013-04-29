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

import os
import interact
import interact._utils as _utils

def check_files_exist(*files):
    """
    Checks to see if the given files provided as arguments exist. They must be
    files as defined by os.path.isfile(). Returns a TestResult.

    The TestResult will be passing if and only if all of the files exist.

    """

    missing_files = [i for i in files if not os.path.isfile(i)]

    result = interact.TestResult(
        brief = "This test ensures that all of the necessary files are "
                "present.",
        default_message = "Great job! All the necessary files are present."
    )

    if missing_files:
        result.add_message(interact.TestResult.Message(
            "You are missing {missing_files_}.",
            missing_files_ = _utils.pretty_list(missing_files),
            missing_files = missing_files,
            dscore = -1,
            type = "interact/filesexist/basic_files_exist"
        ))
        result.set_passing(False)
    else:
        result.set_passing(True)

    return result
