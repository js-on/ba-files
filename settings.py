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
"""Settings and data store for mail analysis
"""
import json
import re
with open("data/denylist.txt", "r", encoding="utf-8") as f:
    mail_denylist = list(f.read().splitlines())
with open("data/allowlist.txt", "r", encoding="utf-8") as f:
    mail_allowlist = list(f.read().splitlines())
with open("data/spam.txt", "r", encoding="utf-8") as f:
    buzzwords_spam = list(f.read().splitlines())
with open("data/evil.txt", "r", encoding="utf-8") as f:
    buzzwords_evil = list(f.read().splitlines())
with open("data/blocked_subject.txt", "r", encoding="utf-8") as f:
    subject_blocklist = list(f.read().splitlines())
with open("data/mail_providers.txt", "r", encoding="utf-8") as f:
    mail_providers = f.read().splitlines()
with open("data/most_abused_tlds.txt", "r", encoding="utf-8") as f:
    abused_tlds = f.read().splitlines()
with open("data/typosquatted.json", "r", encoding="utf-8") as f:
    typosq = json.load(f)
mail_ports = [110, 143, 993, 995]
money = re.compile(r'.*[\$€\d][\d\.\,]*[\$€]?.*')
languages = {
    "de": ["de-DE", "german"],
    "en": ["en-GB", "english"]
}

override_dict = {
    'SPF_override_none': 'spf-none',
    'SPF_override_neutral': 'spf-neutral',
    'SPF_override_pass': 'spf-pass',
    'SPF_override_fail': 'spf-fail',
    'SPF_override_softfail': 'spf-softfail',  # disable-secrets-detection
    'SPF_override_temperror': 'spf-temperror',
    'SPF_override_perm': 'spf-permerror',
    'DKIM_override_none': 'dkim-none',
    'DKIM_override_pass': 'dkim-pass',
    'DKIM_override_fail': 'dkim-fail',
    'DKIM_override_policy': 'dkim-policy',
    'DKIM_override_neutral': 'dkim-neutral',  # disable-secrets-detection
    'DKIM_override_temperror': 'dkim-temperror',
    'DKIM_override_permerror': 'dkim-permerror',
    'DMARC_override_none': 'dmarc-none',
    'DMARC_override_pass': 'dmarc-pass',
    'DMARC_override_fail': 'dmarc-fail',
    'DMARC_override_temperror': 'dmarc-temperror',
    'DMARC_override_permerror': 'dmarc-permerror',
}
reputation = {
    "Suspicious": 1,
    "Pass": 0,
    "Fail": 2
}
