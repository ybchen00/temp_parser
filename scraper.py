import csv
import re
import datetime
#import pytz
import requests
import os
#import pandas as pd
from numpy import numpy as np
from bs4 import BeautifulSoup
import scraperwiki

URL="https://my.nycha.info/PublicSite/Transparency/IndoorTemp"
page=requests.get(URL)
content=page.content
soup=BeautifulSoup(content, 'html5lib')

def neat_table(soup):
  table = soup.find('table', {'class':'WEMSmain'})
  if not table:
    return

  # Step 1. Get headers
  headers = []
  for h in table.find('tr').find_all('th'):
    headers.append(''.join(h.findAll(text=True)))
  #print(headers)
  # Prints ['Borough', 'Development', 'Total Apartments', 'Online Sensors', 'Daytime Exceptions (6:00am to 10:00pm)', 'Nighttime Exceptions (10:00pm to 6:00am)']

  # Step 2. Get body
  rows = []
  for r in table.find('tbody').find_all('tr'):
    r = r.find_all(['td', 'th'])
    rows.append(r)

  #print(rows)

  # Step 3. Get rid of HTML tags in body
  clean = []
  for row in rows:
    clean_r = []
    for item in row:
      clean_r.append(''.join(item.findAll(text=True)))
    clean.append(clean_r)

  #print(clean)

  # Step 4. Merge 'Borough' singular rows into the appropriate actual row
  final = []
  for i in range(len(clean)):
    if(len(clean[i]) == 5):
      clean[i] = [''] + clean[i]
    if (len(clean[i]) == 1):
      clean[i][0] = re.sub('\s+',' ',clean[i][0]).strip()
      clean[i+1] = clean[i] + clean[i+1]
    else:
      final.append(clean[i])
  #print(final)

  # Step 5. Put into df!! :)
  df = pd.DataFrame.from_records(final, columns=headers)
  df = df.replace(r'^\s*$', np.nan, regex=True)
  df = df.fillna(method='ffill')
  display(df)
  d = df.to_dict('records')
  return d

dict_list = neat_table(soup)
for d in dict_list:
  print(d)
  scraperwiki.sqlite.save(unique_keys=['Development'], data=d)
