# liquibase_diffs.py
# @author tberg
# @date 01.19.2016
#
# Simple script to pull down all the "Change" types from the liquibase documentation
# and roll through grabbing each documentation page to see if the change is supported
# in both Oracle and PostgreSQL.  Turns out, only addAutoIncrement is not supported in
# both.  In Oracle, you use a sequence and a trigger instead of auto incrementing.
from bs4 import BeautifulSoup
import requests, re

html = requests.get("http://www.liquibase.org/documentation/changes/").text
parsed_html = BeautifulSoup(html, 'html5lib')

links = [l.get('href') for l in parsed_html('a')
         if re.match("[a-z_]+.html", l.get('href'))]

for link in links:
    change_page = requests.get("http://www.liquibase.org/documentation/changes/" + link).text
    parsed_page = BeautifulSoup(change_page, 'html5lib')

    print parsed_page.h1.text
    for tr in parsed_page('tr'):
        if tr.td and re.match("Oracle|PostgreSQL", tr.td.text):
            print tr.td.text, "=", tr.td.next_sibling.text
    print
