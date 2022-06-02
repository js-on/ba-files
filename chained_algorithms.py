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
"""Mail file to run all implemented checks on one mail or a whole folder
"""

from threading import Thread
from typing import List
import time
import glob
import sys

from checks import authenticity_check
from checks import is_from_external
from checks import is_denylisted
# from checks import contains_buzzword
from checks import has_coin_addr
from checks import is_faked_sender
from checks import contains_greeting
from checks import is_unusual_subject
from checks import is_sus_date
from checks import is_domain_working
from checks import check_language_quality
from checks import get_mail_intention
from checks import is_typosquatted

from classes import mailAddr, Content, Headers
from helper import read_eml
from Report.result import Result
from Report.report import Report


headers: list[str] = [
    "eml_name",
    "authenticity_check",
    "is_from_external",
    "is_denylisted",
    # "contains_buzzword",
    "has_coin_addr",
    "is_faked_sender",
    "contains_greeting",
    "is_unusual_subject",
    "is_sus_date",
    "is_domain_working",
    "check_language_quality",
    "get_mail_intention",
    "is_typosquatted"
]

results: List[Result] = []
procs: List[Thread] = []

if len(sys.argv) == 1:
    mails: List[str] = glob.glob("incidents/*.eml")
else:
    mails = [sys.argv[1]]


def run(pid: int = 0):
    """Run all checks

    Args:
        pid (int): Process ID if threaded; defaults to 0
    """
    while mails:
        mail: str = mails.pop(0)
        time_stamp: str = time.strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{time_stamp}] Thread #{pid} :: {mail}")
        eml: dict = read_eml(mail)
        content: Content = Content(eml["Body"])
        mail_headers: Headers = Headers(eml["Headers"])
        mail_addr: mailAddr = mailAddr(mail_headers["From"])

        result: Result = Result(mail)
        result["authenticity_check"] = authenticity_check(mail_headers)
        result["is_from_external"] = is_from_external(mail_headers, mail_addr)
        result["is_denylisted"] = is_denylisted(mail_addr)
        result["has_coin_addr"] = has_coin_addr(content)
        result["is_faked_sender"] = is_faked_sender(mail_addr)
        result["contains_greeting"] = contains_greeting(content, mail_headers)
        result["is_unusual_subject"] = is_unusual_subject(mail_headers)
        result["is_sus_date"] = is_sus_date(mail_headers)
        # INFO: Not mentioned in BA
        # result["contains_buzzword"] = contains_buzzword(content)
        result["is_domain_working"] = is_domain_working(mail_addr)
        result["check_language_quality"] = check_language_quality(content)
        result["get_mail_intention"] = get_mail_intention(content)
        result["is_typosquatted"] = is_typosquatted(mail_addr)

        results.append(result)

# for pid in range(jobs):
#     procs.append(Thread(target=run, args=(pid,)))
# for proc in procs:
#     proc.start()
# for proc in procs:
#     proc.join()


run(0)

report = Report()
report.set_headers(headers)
# Need to reformat data; due to usage of a stupid custom class
data = [[result.mail] + result.values() for result in results]
report.set_data(data)
if len(sys.argv) == 1:
    report.save("report.xlsx")
    report.as_csv("report.csv", sep=";")
else:
    row = results[0].data()
    for k in row:
        v = results[0].row[k]
        print(f"{k} :: {v}")
