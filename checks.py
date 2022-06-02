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
"""Documented analysis algorithms from the BA

Returns:
    _type_: Analysis methods
"""
from datetime import datetime
from threading import Thread
import socket
import re
from difflib import SequenceMatcher
from textblob_de import TextBlobDE
from textblob import TextBlob
from fuzzywuzzy import fuzz
import language_tool_python
import langdetect
import nltk
from settings import reputation, mail_denylist, mail_allowlist
from settings import buzzwords_evil, buzzwords_spam, subject_blocklist
from settings import mail_providers, mail_ports, languages, abused_tlds, typosq, money
from helper import dist_split, fmt_displ_name, fmt_local_part, debug, levenshteinDist
from authenticity import check_spf, check_dkim, check_dmarc, auth_check
from classes import Headers, Content, mailAddr
from emojis import EMOJIS

RESULTS = {}


def authenticity_check(headers: Headers) -> float:
    """check authenticity of headers (done by XSOAR) Source:
    https://github.com/demisto/content/blob/e1c26879d309aa84c5aa27c30a0ff3bc4f7905d8/Packs/Phishing/Scripts
    /CheckEmailAuthenticity/CheckEmailAuthenticity.py
    :param headers: incident context
    :return: score
    """
    auth = headers["Authentication-Results"]
    spf = headers["Received-SPF"]
    # msg_id = headers["Message-ID"]
    if not auth and not spf:
        # Authenticity is Undetermined
        return 1
    spf_data = check_spf(auth, spf)
    dkim_data = check_dkim(auth)
    dmarc_data = check_dmarc(auth)
    authenticity = auth_check(spf_data, dkim_data, dmarc_data)
    return reputation[authenticity]


def is_from_external(headers: dict, mail: mailAddr) -> float:
    """Check if mail is from external sender
    :param headers: mail headers
    :param mail: mail address
    :return: score
    """
    if "[EXT]" in headers["Subject"] and mail["domain"] not in mail_allowlist:
        return 1
    return 0


def contains_questions(rawtext: Content) -> float:
    """calculate ratio of questions based on punctuation
    :param rawtext: mail content
    :return: ratio
    """
    sentences = rawtext.count(".")
    questions = rawtext.count("?")
    return questions / (sentences + questions) * 3


def is_denylisted(mail: mailAddr) -> float:
    """check if mail domain is denylisted
    :param mail: incident context
    :return: score
    """
    if mail["empty"]:
        return 0
    elif mail["domain"] in mail_denylist:
        return 1
    elif mail["domain"] in mail_allowlist:
        return 0
    else:
        return 0


def contains_buzzword(rawtext: Content) -> float:
    """Check if mail content contains specific buzzwords
    :param rawtext: mail content
    :return: buzzword score
    """
    text = rawtext.lower()
    score = 0
    for word in buzzwords_evil:
        word = word.lower()
        word_len = len(word.split(" "))
        split_text = dist_split(text, word_len)
        similarity = max([fuzz.ratio(word, st) for st in split_text])
        if similarity >= 90:
            score += 2
        elif similarity >= 70:
            score += 1
    for word in buzzwords_spam:
        word = word.lower()
        word_len = len(word.split(" "))
        split_text = dist_split(text, word_len)
        similarity = max([fuzz.ratio(word, st) for st in split_text])
        if similarity >= 90:
            debug("80% " + word)
            score += 1
        elif similarity >= 70:
            debug("50% " + word)
            score += 0.5
    for mail in mail_denylist:
        if mail in text:
            score += 0.5
    return score


def has_coin_addr(content: Content) -> float:
    """check if crypto money IOC exists
    :param rawtext: mail content
    :return: score
    """
    score = 0
    words = dist_split(str(content), dist=1)
    for word in words:
        if re.match(r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$', word):
            # contains BTC addr
            # score += 10
            score += 1
        if re.match(r'^4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$', word):
            # contains Monero addr
            # score += 10
            score += 1
    return score


def is_faked_sender(email: mailAddr) -> float:
    """calculate difference between displayed sender name
    and the name within the mail addrs local path
    :param email: mail object
    :return: score
    """
    if email["empty"]:
        return 0
    scores = []
    display_names = list(
        set([email["displayName"], fmt_displ_name(email["displayName"])]))
    local_parts = list(set([
        email["localPart"],
        fmt_local_part(email["localPart"]),
        fmt_local_part(email["localPart"], repl=" ")
    ]))
    for display_name in display_names:
        if display_name == "":
            continue
        for local_part in local_parts:
            scores.append(SequenceMatcher(
                None, display_name.lower(), local_part.lower()).ratio())
    score = max(scores) if scores else 1
    return abs(1 - score) * 10


def contains_greeting(text: Content, headers: Headers) -> float:
    """Check if mail contains personal greeting of sender and/or recipient
    :param rawtext: Mail content

    Args:
        text (Content): Mail content
        headers (Headers): Mail headers

    Returns:
        float: Sum of highest matching ratio for first- and lastname
    """
    text = str(text)
    sender = mailAddr(headers["From"])
    # Fix issue with non existing From/To Header
    if not sender:
        sender = []
    rcpt = mailAddr(headers["To"])
    if not rcpt:
        rcpt = []
    lang = langdetect.detect(text)
    words = nltk.word_tokenize(
        text, language=languages.get(lang, ["en-GB", "english"])[1])
    first = words[:round(len(words)/10)]
    last = words[len(words)-round(len(words)/10):]
    scores = {"last": [], "first": []}
    for word in first:
        scores["first"].append(SequenceMatcher(
            None, sender.get("lastname", "").lower(), word.lower()).ratio())
        scores["first"].append(SequenceMatcher(
            None, sender.get("firstname", "").lower(), word.lower()).ratio())
    for word in last:
        scores["last"].append(SequenceMatcher(
            None, rcpt.get("lastname", "").lower(), word.lower()).ratio())
        scores["last"].append(SequenceMatcher(
            None, rcpt.get("firstname", "").lower(), word.lower()).ratio())

    return max(scores["last"]) + max(scores["first"])


def is_unusual_subject(headers: Headers) -> int:
    """Check if mail has suspicious subject

    Args:
        headers (Headers): Mail headers

    Returns:
        int: Calculated reputation
    """
    subject = headers["Subject"]
    score = 0
    if money.match(subject):
        score += 2
    if levenshteinDist(subject, subject.upper()) <= len(subject)*.25:
        score += 2
    for char in subject:
        if ord(char) in EMOJIS:
            score += 0.5
    for word in subject.split(" "):
        if word in subject_blocklist:
            score += 1
    return score


def is_sus_date(headers: Headers) -> int:
    """Check if sender date is suspicious

    Args:
        headers (Headers): Mail headers

    Returns:
        int: Rating
    """
    date = headers["Date"]
    if date.endswith(")"):
        date = date.split(" (")[0]

    date_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    score = 0
    if date_obj.weekday in [5, 6]:
        score += 1
    if date_obj.hour <= 6 or date_obj.hour >= 18:
        score += 1

    return score


def __is_port_open(ip_addr: str, port: int) -> bool:
    """Helper function to check for open port

    Args:
        ip_addr (str): IP address
        port (int): Port

    Returns:
        bool: Whether port is open or not
    """
    global RESULTS
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    res = sock.connect_ex((ip_addr, port))
    RESULTS[port] = int(not bool(res))


def is_domain_working(mail: mailAddr) -> bool:
    """Check if domain exists and is able to receive mails

    Args:
        mail (mailAddr): Mail address object

    Returns:
        bool: Whether domain is functional or not
    """
    domain = mail["domain"]
    if domain in mail_providers:
        return 1
    try:
        ip_addr = socket.gethostbyname(domain)
    except socket.gaierror:
        return 0
    procs = []
    for port in mail_ports:
        procs.append(Thread(target=__is_port_open, args=(ip_addr, port, )))
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()

    return int(True in RESULTS.values())


def check_language_quality(text: Content) -> float:
    """Check quality of content via LanguageTool

    Args:
        text (Content): Content of the mail

    Returns:
        float: Ratio
    """
    text = str(text)
    lang = langdetect.detect(text)
    tool = language_tool_python.LanguageTool(
        languages.get(lang, ["en-GB", "english"])[0])
    sentences = nltk.sent_tokenize(
        text, language=languages.get(lang, ["en-GB", "english"])[1])
    matches = tool.check(text)
    return (100/len(sentences))*len(matches)


def get_mail_intention(text: Content) -> float:
    """Try to figure out the emotions in the mail text

    Args:
        text (Content): Content of the mail

    Returns:
        float: Calculated emotion
    """
    text = str(text)
    lang = langdetect.detect(text)
    if lang == "de":
        blob_text = TextBlobDE(text)
    else:
        blob_text = TextBlob(text)
    pol, subj = [], []
    for sentence in blob_text.sentences:
        sentiment = sentence.sentiment
        pol.append(sentiment.polarity)
        subj.append(sentiment.subjectivity)

    return (abs(sum(pol))+abs(sum(subj)))/len(blob_text.sentences)


def is_typosquatted(mail: mailAddr) -> int:
    """Check if mail domain could be typosquatted

    Args:
        mail (mailAddr): Mail address object

    Returns:
        int: Number of possible typosquatted domains
    """
    domain = mail["domain"]
    tld = "." + domain.split(".")[1]
    res = {}
    for abused in abused_tlds:
        data = typosq[abused]
        if bool(sum([1 if tld in values
                    else 0
                    for values in data.values()])):
            res[abused] = data

    return len(res)
