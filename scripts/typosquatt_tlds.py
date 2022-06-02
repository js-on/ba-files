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

from fuzzywuzzy import fuzz
import json

sm = fuzz.SequenceMatcher()

tlds = open("data/tlds.txt", "r").read().splitlines()
tlds = [tld for tld in tlds if not "&" in tld]
res = {}
length = len(tlds)
for i, tld in enumerate(tlds):
    print(f"Progress: {i}/{length} ...", end='\r')
    threshold = int(.3*len(tld))
    res[tld] = {}
    for squatted in tlds:
        if squatted == tld:
            continue
        sm.set_seqs(tld, squatted)
        if sm.distance() <= threshold:
            if not threshold in res[tld].keys():
                res[tld][threshold] = [squatted]
            else:
                res[tld][threshold].append(squatted)

print("\nExporting data to 'data/typosquatted.json' ...")
json.dump(obj=res, fp=open("../data/typosquatted.json", "w"), indent=4)