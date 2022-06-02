Files for my Bachelors Thesis
===
## About
Submitted to Leibniz University of Applied Sciences and the examiners Prof. Dr. Oleg Lobachev and Prof. Dr. Michael Arnold.

Contact me with any questions at Vorname.Nachname@leibniz-fh.de.

> Hint: Some code uses Python 3.10 specific syntax!

## Files
### Logic
- *authenticity.py*: Files from XSOAR Content repository to check for SPF/DKIM/DMARC issues
- *chained_algorithms.py*: Concatenates all algorithms to produce final results
- *checks.py*: Contains all checks explained in the thesis
- *classes.py*: Contains some helper classes explained in the thesis
- *emojis.py*: Contains list of emojis
- *helper.py*: Contains some helper methods
- *settings.py*: Contains several lists/objects to be used by the algorithms
### Data
- *data/allowlist.txt*: Store allowed mail sender domains
- *data/blocked_subject.txt*: Store keywords blocked in subject
- *data/denylist.txt*: Store mail sender domains which are not allowed
- *data/emojis.txt*: Store unicode blocks of emojis
- *data/evil.txt*: Store words which are not allowed in mail body
- *data/mail_providers.txt*: List of all (active) mail provider domains
- *data/most_abused_tlds.txt*: List of most abused top level domains (TLDs)
- *data/tlds.txt*: List of all available TLDs
- *data/typosquatted.json*: Correlation of similar TLDs for most abused TLDs
- *data/weights.json*: Weights for each algorithm (not in use; see TODO.md)
### Scripts
- *scripts/csv2tex.py*: Convert CSV output to TEX
- *scripts/emojis_to_list.py*: Generate Python list object from *data/emojis.txt*
- *scripts/mail_providers.py*: Download mail providers and remove inactive ones
- *scripts/typosquatt_tlds.py*: Create TLD typosquatting correlations
### Results
- *report_with_class.csv*: CSV output with long class names
- *report_with_short_class.csv*: CSV output with abbreviated class names (explaind in thesis)
- *report.xlsx*: Auto generated excel report (not optimized)
### Incidents
> Contains .eml files to be analyzed; not included in this repo for obvious reasons!
### Others
- *TODO.md*: Contains tasks to be done; not finished
- *requirements.txt*: Contains all requirements to be installed
- *README.md*: Nothing here but crickets... `¯\_(ツ)_/¯`

## Libraries
| Name | Version | License |
| ---- | ------- | ------- |
| beautifulsoup | 4.11.1 | MIT License (MIT) |
| colorama | 0.4.4 | BSD License (BSD) |
| fuzzywuzzy | 0.18.0 | GNU General Public License v2 (GPLv2) |
| langdetect | 1.0.9 | Apache Software License (MIT) |
| language_tool_python | 2.7.0 | GNU GPL |
| nltk | 3.7 | Apache Software License (Apache License, Version 2.0) |
| openpyxl | 3.0.9 | openpyxl==3.0.9
| requests | 2.27.1 | Apache Software License (Apache 2.0) |
| roman | 3.3 | Python Software Foundation License (Python 2.1.1) |
| textblob | 0.17.1 | MIT License (MIT) |
| textblob_de | 0.4.3 | MIT License (MIT) |
| urllib3 | 1.26.8 | MIT License (MIT) |


## Copyright
This is WIP and may not be maintained in future. This was just for scientific purposes and may be adapted for productive usage within internal systems.