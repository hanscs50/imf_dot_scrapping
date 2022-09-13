
# default URL# -*- coding: utf-8 -*-
# """
# Created on Mon Sep 12 10:46:29 2022
#
# @author: stefa
# """
#
import requests
import pandas as pd
url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/'

# list of country codes: https://www.nationsonline.org/oneworld/country_code_list.htm
# you can read more here: https://briandew.wordpress.com/category/python/

key = 'CodeList/CL_AREA_DOT'
# example 0
# Obtain country codes
# Dimension: 2: CL_AREA_DOT
# URL: https://briandew.wordpress.com/2016/05/01/machine-reading-imf-data-data-retrieval-with-python/
country = requests.get(f'{url}{key}').json()
df = pd.DataFrame(country['Structure']['CodeLists']['CodeList']['Code'])
print(df)

## get country_codes into a list and panda.series
country_codes = df['@value']
country_codes = [x for x in country_codes if not any(x1.isdigit() for x1 in x)]
print(country_codes)
country_codes = sorted(country_codes)
#country_codes = country_codes[:-1]
#country_codes = [value for value in country_codes2 if type(value) == str]
country_codes = pd.Series(data=country_codes)
## delete all codes containing numbers
country_codes = country_codes.astype(str).values.tolist()
print(country_codes)
# delete last observation '_X'
country_codes = country_codes[:-1]

## create string for URL
country_codes_str = '+'.join((str(n) for n in country_codes))
print(country_codes_str)

# Obtain country codes
x = 0;
while x < 247:
    if df['@value'][x] is None:
        break
    items = (str(df['@value'][x]), str(df['Description'][x]['#text']))     
    print(': '.join(items))
    x += 1;
    
########### this shows the values of the 'data' set which still contains all 
########### numeric codes as well. How to adapt 'data' set?

###-----------------------------------------------------------------------#####

# #### attempt to create one loop (perhaps better as function?)
# ## create csvs for every country export to all counterpart areas (=importer)
# i = -1
# j = 0
# ## length of country_code is 216
# while j < 216:
#     i += 1
#     j += 1
#     ## select exporter
#     exporter = country_codes[i]
#     print("Exporting country:" + " " + exporter)       
          
#     param = [('dataset', 'DOT'),
#               ('freq', 'A'),
#               # loop through country codes
#               ('country', exporter),
#               ('series', 'TXG_FOB_USD'),
#               ('counterpart_area', counter),  # can adapart here, but not every pair exists;
#         # how can I skip pairs that do not exist in the JSON file?
#               #('start', '?startPeriod=1948')]   ## not needed
#     series = '.'.join([i[1] for i in param[1:4]])
#     print(series)

#     key = f'CompactData/{param[0][1]}/{series}{param[-1][1]}'

#     print(f'{url}{key}')  # STEFAN! URL can be changed at the end and pass country codes you want:
#     # Combine API url with key specific to data request
#     data = requests.get(f'{url}{key}').json()    ## ISSUE: when exporter-importer pairs does not exist: line 1 column 1 (char 0)

#     #Convert results to pandas dataframe
#     # SOUFIANE: How can I create differently named dataframes? first iteration df_k = df_AF
#     df = pd.DataFrame({s['@COUNTERPART_AREA'] : {pd.to_datetime(i['@TIME_PERIOD']) : 
#       round(float(i['@OBS_VALUE']), 1) for i in s['Obs']} 
#       for s in data['CompactData']['DataSet']['Series']})

###-----------------------------------------------------------------------#####

## simplified attempt; all exporter country pairs with US and Canada


x = 0;
while x < 247:
    country = country_codes[x]
    x += 1
    key = f'CompactData/DOT/A.{country}.TXG_FOB_USD.US+CA'
    print(key)
    #if country == "AS" or country == "AW":
    #    continue
    #else:
    # different data sets
    #data = country + '_export' # the name for the dataframe
    #filename = "data_{}.json".format(country)
    try:
        # Retrieve data from IMF API
        data = requests.get(f'{url}{key}').json()
        # Convert results to pandas dataframe ---> how to create a separate dataframe for every country?
        df = pd.DataFrame({s['@COUNTERPART_AREA'] : {pd.to_datetime(i['@TIME_PERIOD']) :
         round(float(i['@OBS_VALUE']), 1) for i in s['Obs']}
         for s in data['CompactData']['DataSet']['Series']})
    except:
        print(f'Problem getting {url}{key}')
##### SOUFIANE EXAMPLE:
##### CompactData/DOT/A.AS.TXG_FOB_USD.US+CA --> AS-US or AS-CA (AS = American Samoa); apparently, there is not data for one of those two pairs -- how do I determine whether
# the JSON file contains the pair and how can I automatically skip it if it is not in 'data'?


## Double loop  CONT HERE
test = pd.DataFrame()

for x in country_codes[:1]:
    print(f'x is {x}')
    for y in country_codes:
        print(f'y is {y}')
        if not x == y:
            key = f'CompactData/DOT/A.{x}.TXG_FOB_USD.{y}'
            try:
                data = requests.get(f'{url}{key}').json()
                #df = pd.DataFrame({s['@COUNTERPART_AREA'] : {pd.to_datetime(i['@TIME_PERIOD']) :
                # round(float(i['@OBS_VALUE']), 1) for i in s['Obs']}
                # for s in data['CompactData']['DataSet']['Series']})
                oneSerie = data['CompactData']['DataSet']['Series']
                for i in data['CompactData']['DataSet']['Series']['Obs']:
                    df = pd.DataFrame({oneSerie['@COUNTERPART_AREA'] : {pd.to_datetime(i['@TIME_PERIOD']): round(float(i['@OBS_VALUE']), 1)}})
                    test.append(df)    ## name df differently, and create new columns
                    print(f'Success with {y}')
            except:
                print(f'Error in {url}{key}')


## how to comment out on a germany keyboard?