# Copyright 2022 Jakob Schaffarczyk
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
"""_summary_
"""
class Result:
    """_summary_
    """
    def __init__(self, fname: str):
        """_summary_

        Args:
            fname (str): _description_
        """
        self.mail = fname
        self.data_ = {}

    def __getitem__(self, key):
        """_summary_

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.data_.get(key, None)

    def __setitem__(self, key, val):
        """_summary_

        Args:
            key (_type_): _description_
            val (_type_): _description_
        """
        self.data_[key] = val

    def data(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        return self.data_

    def values(self) -> list:
        """_summary_

        Returns:
            list: _description_
        """
        return list(self.data_.values())

    def keys(self) -> list:
        """_summary_

        Returns:
            list: _description_
        """
        return list(self.data_.keys())
