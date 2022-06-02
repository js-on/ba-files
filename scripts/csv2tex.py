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

"""Convert CSV report with short class names and categories to tex table
"""

import roman
import json
import sys

def __parse_number(number: str) -> int | float | str:
    """internal: Set correct type for int/float after reading from file.

    Args:
        number (str): Number as string

    Returns:
        int|float|str: Number with correct type; str if no conversion possible
    """
    try:
        return int(number)
    except ValueError:
        pass
    try:
        return float(number)
    except:
        return number

colours = {
    "Newsletter": "green",
    "Phishing": "red",
    "Unknown": "orange",
    "Spam": "orange",
    "Fraud": "red",
    "Sextortion": "red",
    "Business": "green"
}

with open("Report/settings.json", 'r', encoding="utf-8") as f:
    val_color = json.load(f)

with open(sys.argv[1], 'r', encoding="utf-8") as f:
    csv = f.read().splitlines()

filecontents = []
for line in csv:
    row = []
    for i, val in enumerate(line.split(",")):
        head = csv[0].split(",")[i]
        try:
            conf = val_color["short"][head]
        except:
            conf = {}
        val = __parse_number(val)
        if isinstance(val, float):
            val = round(val, 2)
        if not isinstance(val, str):
            if val >= conf["threshold"]:
                val = r"\textcolor{" + conf["higher"] + r"}{" + str(val) + r"}"
            else:
                val = r"\textcolor{" + conf["lower"] + r"}{" + str(val) + r"}"
        else:
            if val in colours:
                val = r"\textcolor{" + colours[val] + "}{" + val + "}"
        row.append(val)
    filecontents.append(','.join(row))

headers = r"\bfseries " + r" & \bfseries ".join(csv[0].split(","))

csvcol = "&".join([r"\csvcol" + roman.toRoman(i).lower() for i in range(1,csv[0].count(",")+2)])

print(r"\begin{filecontents*}{Analysis.csv}")
for line in filecontents:
    print("\t" + line)
print(r"\end{filecontents*}")
print()
print(r"\begin{tabular}{" + '|'.join(["l" for _ in range(csv[0].count(",")+1)]) + "}%")
print(headers)
print(r"\csvreader[head to column names]{Analysis.csv}{}%")
print(r"{\\\hline" + csvcol + r"}")
print(r"\end{tabular}")
