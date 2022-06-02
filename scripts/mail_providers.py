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

import requests
from threading import Thread
import socket
from time import sleep, time

jobs = 24
PROVIDER = []

print(f"[ ] downloading data", end='\r')
data = requests.get("https://raw.githubusercontent.com/edwin-zvs/email-providers/master/email-providers.csv").text.splitlines()
print(f"[*] downloading data")

def run() -> None:
    global PROVIDER
    while data:
        domain = data.pop(0)
        try:
            socket.gethostbyname(domain)
            PROVIDER.append(domain)
        except socket.gaierror:
            pass
    return

def status():
    size = len(data)
    while data:
        print(f"[ ] Checked {size-len(data)}/{size} domains ...", end='\r')
        sleep(1)
    print(f"[*] Checked {size}/{size} domains ...")
    return

t1 = time()
procs = []
Thread(target=status).start()
for _ in range(jobs):
    procs.append(Thread(target=run))
for proc in procs:
    proc.start()
for proc in procs:
    proc.join()

print("[ ] write results to mail_providers.txt", end='\r')
with open("../data/mail_providers.txt", 'w') as f:
    f.write('\n'.join(sorted(PROVIDER)) + "\n")
print("[*] write results to data/mail_providers.txt")
t2 = time()

print(f"Took: {round(t2-t1, 2)}s ...")