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
"""Classes for mail analysis

Returns:
    _type_: Classes for mail analysis
"""
from email.header import decode_header
from typing import List, Union, Any
import re


class Headers:
    """class to allow easy key/value access on
    json object with email headers
    TODO: Type for email (Message) not set

    Returns:
        Headers: Header class
    """

    def __init__(self, msg):
        """Init mail header object for easy header access

        Args:
            msg (_type_): Mail object (?)
        """
        self.headers: dict = {}
        for key in msg.keys():
            val, encoding = decode_header(msg.get(key))[0]
            if isinstance(val, bytes):
                if encoding is None:
                    encoding = "utf-8"
                val = val.decode(encoding)
            self.headers[key] = val

    def __getitem__(self, key: str, default: Any = None) -> Union[dict, list, str, int, None]:
        """Get value from header

        Args:
            key (str): Key
            default (Any, optional): Default value. Defaults to None.

        Returns:
            Union[dict, list, str, int, None]: Value
        """
        try:
            return self.headers[key]
        except KeyError:
            val = default
        return val

    def get(self, key: str, default: Any = None) -> Union[dict, list, str, int, None]:
        """_summary_

        Args:
            key (str): Key
            default (Any, optional): Default value. Defaults to None.

        Returns:
            Union[dict, list, str, int, None]: Value
        """
        try:
            val = self.headers[key]
        except KeyError:
            val = default
        return val

    def keys(self) -> List[str]:
        """Return all keys from object

        Returns:
            List[str]: List of keys
        """
        return list(self.headers.keys())


class mailAddr:
    """Class for handling mail addresses
    """
    def __init__(self, mail: str):
        """Init mail address object

        Args:
            mail (str): Mail address (header["From"] or header["To"])
        """
        self.empty = bool(not mail or not "@" in mail)
        if not self.empty:
            if "<" in mail and ">" in mail:
                self._address = mail.split("<")[1].strip(">").lower()
            else:
                self._address = mail
            self._local_part = self._address.split("@")[0].lower()
            self._domain = self._address.split("@")[1].lower()
            if "<" in mail:
                self._displ_name = mail.split("<")[0].strip().lower()
            else:
                self._displ_name = ""
            if "." in self._local_part:
                self._first_name = self._local_part.split(".")[0].lower()
                self._last_name = self._local_part.split(".")[1].lower()
            else:
                self._first_name = self._local_part
                self._last_name = ""
            self._parts = {
                "address": self._address,
                "localPart": self._local_part,
                "domain": self._domain,
                "displayName": self._displ_name,
                "firstname": self._first_name,
                "lastname": self._last_name,
                "empty": self.empty
            }
        else:
            self._parts = {}

    def __getitem__(self, key: str) -> str:
        """Get item from mail addr object

        Args:
            key (str): Key

        Returns:
            str: Value
        """
        try:
            if self.empty:
                return None
            return self._parts[key]
        except KeyError:
            raise Exception from KeyError(f"Key '{key}'' does not exist.")

    def get(self, key: str, default: Any = None) -> str:
        """_summary_

        Args:
            key (str): Key
            default (Any): Default value

        Returns:
            str: Value
        """
        return self._parts.get(key, default)

    def __str__(self) -> str:
        """Return object as string

        Returns:
            str: Object as string
        """
        return self._address

    def __repr__(self) -> str:
        """Return object as string

        Returns:
            str: Object as string
        """
        return self._address


class Content:
    """Class for handling mail content
    """

    def __init__(self, content: str):
        """Class to organize mail content; nsfw atm

        Args:
            content (str): Mail content
        """
        self._content = self.format_content(content).lower()
        self._words = self.extract_words()
        self._sentences = self.extract_sentences()

    def format_content(self, content: str) -> str:
        """Format content and remove too many whitespaces

        Args:
            content (str): Mail content

        Returns:
            str: Formatted mail content
        """
        content = re.sub(r'[ \t]+', r' ', content)
        return content

    def count(self, char: str) -> int:
        """Count occurrence of char in content

        Args:
            char (str): Character to search for

        Returns:
            int: Count of character occurence
        """
        return self._content.count(char)

    def lower(self) -> str:
        """Return content in lower case

        Returns:
            str: Mail content
        """
        return self._content.lower()

    def extract_words(self) -> list:
        """WIP

        Returns:
            list: WIP
        """
        return []

    def extract_sentences(self) -> list:
        """WIP

        Returns:
            list: WIP
        """
        return []

    def startswith(self, start: str) -> bool:
        """Check if content startswith string

        Args:
            s (str): Start substr

        Returns:
            bool: Whether strings starts with substr or not
        """
        return str(self).startswith(start)

    def __repr__(self):
        """Return object as string

        Returns:
            str: Object as string
        """
        return self._content

    def __str__(self):
        """Return object as string

        Returns:
            str: Object as string
        """
        return self._content

    def __getitem__(self, key: str):
        """Get values from Content
        Args:
            key (str): Key; one of words|sentences
        Raises:
            Exception: Key does not exist
        Returns:
            Any: Value
        """
        if key == "words":
            return self._words
        elif key == "sentences":
            return self._sentences
        else:
            raise Exception(f"Key '{key}' does not exist.")
