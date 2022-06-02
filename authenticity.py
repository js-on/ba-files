"""Authenticity checks from XSOAR Phishing Content Pack

Returns:
    _type_: SPF,DMARC,DKIM validation methods
"""
import re
from typing import Dict, Union, Any
from settings import override_dict


def check_spf(auth: str, spf: str) -> Dict[str, Union[str, Any]]:
    """Check SPF results
    :param auth: Authentication results
    :param spf: SPF header
    :return: parsed SPF results
    """
    spf_context = {
        'Validation-Result': 'Unspecified',
        'Sender-IP': 'Unspecified',
        'Reason': 'Unspecified'
    }
    spf = spf.replace("\n", "")
    if auth is None:
        spf_context['Validation-Result'] = spf.split(' ')[0].lower()
        sender_ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', spf)
    else:
        result = re.search(r'spf=(\w+)', auth)
        if result is not None:
            spf_context['Validation-Result'] = result.group(1).lower()
        sender_ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', auth)
    if sender_ip:
        spf_context['Sender-IP'] = sender_ip[0]
    if spf is not None:
        spf_context['Reason'] = re.findall(r'\((.+)\)', spf)[0]
    return spf_context


def check_dkim(auth: str) -> Dict[str, Union[str, list]]:
    """Check DKIM results
    :param auth: Authentication results
    :return: parsed DKIM results
    """
    dkim_context = {
        "Validation-Result": "Unspecified",
        "Signing-Domain": "Unspecified",
        "Reason": "Unspecified"
    }
    if auth is not None:
        result = re.search(r'dkim=(\w+)', auth)
        if result:
            dkim_context["Validation-Result"] = result.group(1)[0]
        reason = re.search(r'dkim=\w+ \((.+?)\)', auth)
        if reason:
            dkim_context["Reason"] = reason.group(1)
        domain = re.findall(r'dkim=[\w\W]+[=@](\w+\.[^ ]+)', auth)
        if domain:
            dkim_context["Signing-Domain"] = domain
    return dkim_context


def check_dmarc(auth: str) -> Dict[str, Union[str, Dict[str, str], dict]]:
    """Check DMARC results
    :param auth: Authentication results
    :return: Parsed DKIM results
    """
    dmarc_context = {
        "Validation-Result": "Unspecified",
        "Tags": {"Unspecified": "Unspecified"},
        "Signing-Domain": "Unspecified"
    }
    if auth is not None:
        result = re.search(r'dmarc=(\w+)', auth)
        if result is not None:
            dmarc_context['Validation-Result'] = result.group(1).lower()
        reason = re.findall(r'dmarc=\w+ \((.+?)\)', auth)
        if reason:
            tags = reason[0]
            tags_data = {}
            for tag in tags.split(' '):
                values = tag.split('=')
                tags_data[values[0]] = values[1]
            dmarc_context['Tags'] = tags_data
        domain = re.findall(r'dmarc=.+header.from=([\w-]+\.[^; ]+)', auth)
        if domain:
            dmarc_context['Signing-Domain'] = domain[0]
    return dmarc_context


def auth_check(spf_data, dkim_data, dmarc_data) -> Dict[str, str]|str:
    """Check authenticity of SPF, DKIM and DMARC

    Args:
        spf_data (_type_): parsed SPF data
        dkim_data (_type_): parsed DKIM data
        dmarc_data (_type_): parsed DMARC DATA

    Returns:
        Dict[str, str]|str: Overall analysis result
    """
    spf = spf_data.get("Validation-Result")
    dmarc = dmarc_data.get("Validation-Result")
    dkim = dkim_data.get("Validation-Result")

    if f"spf-{spf}" in override_dict:
        return override_dict.get(f"spf-{spf}")
    if f"dkim-{dkim}" in override_dict:
        return override_dict.get(f"dkim-{dkim}")
    if f"dmarc-{dmarc}" in override_dict:
        return override_dict.get(f"dmarc-{dmarc}")

    if "fail" in [spf, dkim, dmarc]:
        ret_val = "Fail"
    elif spf == "softfail" or dkim == "policy":
        ret_val = "Suspicious"
    else:
        ret_val = None
    if ret_val:
        return ret_val
    undetermined = [None, "none", "temperror", "permerror"]
    if dmarc in undetermined or spf in undetermined or dkim in undetermined or dkim == "neutral":
        return "Undetermined"
    return "Pass"
