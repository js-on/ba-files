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
"""Helper methods
"""
from base64 import decodebytes
import email
import re
from typing import Any
import langdetect
import colorama
from colorama import Fore
from bs4 import BeautifulSoup as bs4
from classes import Content, Headers


colorama.init()
EXT_MESSAGE = re.compile(
    r'this[\n\s]*message[\n\s]*is[\n\s]*from[\n\s]*an[\n\s]*external'
    r'[\n\s]*sender[\n\s]*-[\n\s]*be[\n\s]*cautious,'
    r'[\n\s]*particularly[\n\s]*with[\n\s]*links[\n\s]*and[\n\s]*attachments')


def del_ext_message(text: str) -> str:
    """Delete warning if mail is from external sender
    :param text: mail content
    :return: cleaned mail content
    """
    text = re.sub(EXT_MESSAGE, "", text)
    return text


def extract_incident_id(emlname: str) -> str:
    """Extract incident ID from filename
    :param emlname: name of eml file
    :return: incident ID
    """
    incident_id = emlname.split("_")[0]
    return incident_id


def clean_text(text: str, repl: str = "") -> str:
    """Remove punctuation and special chars from text
    :param text: mail content
    :param repl: char used for replacement
    :return: cleaned text
    """
    for char in "!#$%&*+/=?^_`{|}.~,\n\r":
        text = text.replace(char, repl)
    return text


def dist_split(text: str, dist: int) -> list:
    """Split text and return substrings with dist words
    :param text: mail content
    :param dist: length of substring (number of words)
    :return: list with substrings
    """
    text = del_ext_message(text.lower())
    text = clean_text(text, repl=" ").lower()
    split_text = text.split(" ")
    split_text = [w.strip()
                  for w in split_text if not re.match(r'^[\s\t\r\n]*$', w)]
    res = []
    for i in range(0, len(split_text) - dist + 1):
        res.append(' '.join(split_text[i:i+dist]))
    return res


def fmt_local_part(addr: str, repl: str = "") -> str:
    """format local part of mail addr
    :param addr: mail addr
    :param repl: character used for replacement
    :return: formatted local part
    """
    for char in "!#$%&'*+-/=?^_`{|}.~":
        addr = addr.replace(char, repl)
    return addr


def fmt_displ_name(name: str) -> str:
    """format display name
    :param name: display name
    :return: formatted display name
    """
    if "," in name:
        name = ' '.join([i.strip() for i in name.split(",")[::-1]])
    return name


def detect_lang(rawtext: str) -> str:
    """Detect email language
    :param rawtext: Mail content
    :return: Detected language
    """
    try:
        return langdetect.detect(rawtext)
    except Exception as exception:
        raise exception


def read_eml(fname: str) -> dict:
    """Parse Email
    :param fname: filename
    :return: Mail context (headers, body)
    """
    context = {}
    with open(fname, 'rb') as fp:
        msg = email.message_from_binary_file(fp)
        context["Headers"] = Headers(msg)
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                try:
                    body = part.get_payload(decode=True).decode()
                except (AttributeError, UnicodeDecodeError):
                    body = part.get_payload()
                except:
                    print(part.get_payload())
                    for subpart in part.get_payload():
                        try:
                            content_transfer_encoding = subpart["Content-Transfer-Encoding"]
                        except Exception as exception:
                            raise exception from Exception(f"Something went wrong analysing '{fname}'")
                        content_charset = subpart["Content-Type"].split('="')[
                            1][:-1]
                        content_type = subpart["Content-Type"].split("; ")[0]
                        if content_transfer_encoding == "base64" and content_type == "text/plain":
                            body = decodebytes(subpart.get_payload().encode()).decode(
                                content_charset)
                            context["Body"] = Content(body)
                            break
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    context["Body"] = Content(body)
                    break
        else:
            content_type = msg.get_content_type()
            context["Body"] = Content(msg.get_payload(decode=True).decode())
    if context["Body"].startswith("<html>"):
        soup = bs4(str(context["Body"]), "lxml")
        try:
            context["Body"] = soup.get_text()
        except Exception as e:
            debug(str(e))

    context["Body"] = del_ext_message(str(context["Body"]))
    return context


def debug(msg: Any):
    """Print debug message

    Args:
        msg (Any): debug message
    """
    print(f"{Fore.CYAN}>>>{Fore.RESET} {msg}")


def levenshteinDist(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance for two strings

    Args:
        s1 (str): first string
        s2 (str): second string

    Returns:
        int: Calculated Levenshtein distance
    """
    m = len(s1)
    n = len(s2)
    d = [[i] for i in range(1, m+1)]  # d matrix rows
    d.insert(0, list(range(0, n+1)))  # d matrix columns
    for j in range(1, n+1):
        for i in range(1, m+1):
            if s1[i-1] == s2[j-1]:
                substitution_cost = 0
            else:
                substitution_cost = 1
            d[i].insert(j, min(d[i-1][j] + 1,
                               d[i][j-1] + 1,
                               d[i-1][j-1] + substitution_cost))
    return d[-1][-1]
