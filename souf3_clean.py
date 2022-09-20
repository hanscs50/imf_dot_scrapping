# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 10:37:32 2022

@author: stefa
"""

import requests
import pandas as pd
import os
import ast
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
#country_codes_str = '+'.join((str(n) for n in country_codes))
#print(country_codes_str)

# Obtain country codes
x = 0;
while x < 247:
    if df['@value'][x] is None:
        break
    items = (str(df['@value'][x]), str(df['Description'][x]['#text']))     
    print(': '.join(items))
    x += 1;


## Dictionary of dataframes

## dictionary

country_dict = {}
for exp in country_codes:
    for imp in country_codes:
        if exp != imp:
            country_dict["{}-{}".format(exp,imp)] = pd.DataFrame()


t = pd.DataFrame()

for i in country_codes:
    t[i]= []


for x in country_codes:
    #print(f'x is {x}')
    for y in country_codes:
        print(f'x is {x} and y is {y}')
        if not x == y:
            key = f'CompactData/DOT/A.{x}.TXG_FOB_USD.{y}'
            try:
                data = requests.get(f'{url}{key}').json()
                oneSerie = data['CompactData']['DataSet']['Series']
                country_dict["{}-{}".format(x,y)] = pd.DataFrame.from_dict(oneSerie)
            except:
                print(f'Error in {url}{key}:\n')
                #print(data)

 

#country_dict.items()

for i in country_dict:
    value = []
    value_flat = [] 
    time = []
    time_flat = []
    #if i == 'AF':
     #print(country_dict[i]['Obs'])
    if country_dict[i].empty == True:
        print(f'{i} is empty')
        continue
    else:
        try:
            print(f'i is {i}')
            print(f'country_dict[i] is {country_dict[i]}')
            ## export value
            value.append([d.get('@OBS_VALUE') for d in country_dict[i]['Obs']])
            value_flat = [item for sublist in value for item in sublist]
            ## year
            time.append([d.get('@TIME_PERIOD') for d in country_dict[i]['Obs']])
            time_flat = [item for sublist in time for item in sublist]
            #value_flat = pd.Series(value_flat)
            country_dict[i]['Export Values'] = value_flat
            country_dict[i]['Year'] = time_flat
        except:
            print(f'Error in {i}:\n')
    
    break


## remove empty dataframes from dict
country_dict = {k:v for (k,v) in country_dict.items() if not v.empty}

## remove 'Obs' column
for df in country_dict.values():
    #print(df.columns)
    try:
        df.drop('Obs', axis=1, inplace=True)  
        #print(df.columns)
    except:
        print(f'Error in {df}:\n')
  

## save to disk


os.chdir('E:/work_other/UvA IMF DOT/data/python')
for file in country_dict:
    print(file.name)
    country_dict[file].to_csv(f"{file}_IMF.csv")
    
# # clean up not updated frames


directory = 'E:/work_other/UvA IMF DOT/data/python/A-M/wip'
os.chdir(directory)
os.getcwd()

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    df = pd.read_csv(f)
    try:
        df2 = df["Obs"].astype('str')
        df2 = df2.apply(lambda x: ast.literal_eval(x))
        df2 = df2.apply(pd.Series)
        df2['@INDICATOR'] = df['@INDICATOR']
        df2['@COUNTERPART_AREA'] = df['@COUNTERPART_AREA']
        df2['@REF_AREA'] = df['@REF_AREA']
        df2.rename(columns ={'@TIME_PERIOD' : 'year', '@OBS_VALUE' : 'exportvalues'}, inplace=True)
        print(fr'{directory}/{filename}')
        df2.to_csv(fr"{directory}/{filename}")
    except:
         print(f'still error in {filename}')
         
## configure tables with only one obs (different format somehow)

directory = 'E:/work_other/UvA IMF DOT/data/python/A-M/wip'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    print(f)
    df = pd.read_csv(f)
    # check whether really just one year
    if len(df.index) == 3:

        #df2 = pd.DataFrame(columns = ['year', 'exportvalues'])
        print(df.at[2, 'Obs'])
        print(df.iloc[[2], [7]])
        d = {'@REF_AREA': df.at[0,'@REF_AREA'], '@INDICATOR': df.at[0,'@INDICATOR'],
             'COUNTERPART_AREA' : df.at[0,'@COUNTERPART_AREA'], 
             'year' : df.at[2,'Obs'], 'exportvalues' : df.at[1,'Obs']}
        df2 = pd.DataFrame(d, index=[0])
        df2.to_csv(f)
    else:
        print(f'legtnh of {filename} more than 3')


## check whether all csvs marked as empty are indeed empty


directory = 'E:/work_other/UvA IMF DOT/data/python/A-M/empty'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    #print(f)
    df = pd.read_csv(f)
    if df.empty != True:
        print(f'{f} is not empty')
