import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import pandas as pd

# REGEX compiled expressions
tweet_re = re.compile(r'#[a-zA-z]+[0-9]+')

goals_re = re.compile(r'Goal [0-9]+')

des_separator_re = re.compile(r'<div id="subHeadline">')
htmltag_re = re.compile(r'<[^>]*>')
newline_re = re.compile(r'[\n\r]+')

#*****************************************

# FUNCTIONS

# Title
def get_title():
    return soup.find(id = 'headline').get_text().strip()

# Goals
def get_goals():
    if len(r.history) and 'the ocean conference' in soup.title.text.lower():


        other_sgd_ind = home_right_raw.index('Other SDGs')

        other_goals = re.findall(goals_re,home_right_raw[other_sgd_ind:])

        goals_lst = ['Goal 14'] + other_goals

    else:
        goals_raw = soup.find(id='targets')
        goals_lst = [goal.get_text() for goal in goals_raw.findAll('strong')]
        
    return ','.join(goals_lst)

# Partners
def get_partners():
    partner_index = home_right_raw_lst.index('Partners') + 1
    next_index = home_right_raw_lst.index('Ocean Basins') \
                    if len(r.history) and 'the ocean conference' in soup.title.text.lower() \
                    else home_right_raw_lst.index('Countries')
            
    partners = [p.strip() for p in home_right_raw_lst[partner_index:next_index]]
    partners = list(filter(None, partners))
    
    return '; '.join(partners)

# Description
def get_description():
    des_raw = soup.find(id='intro').find('div', attrs={'class':'wrap'})

    temp = str(des_raw)
    
    temp = re.sub(htmltag_re, '', temp)
    temp = re.sub(newline_re, '', temp)
    
    if '<div id="subHeadline">' in temp:
        temp = re.sub(des_separator_re, ' : ', temp)    
        return temp.strip()
    else: 
        return temp.strip()
    
def get_resources():
    resources_raw = soup.find(id='resources')
    resources_lst = []

    for resource in resources_raw.findAll('div', recursive = False):
        temp = resource.get_text()

        if temp != '':
            temp = re.sub(r'\n+', ' : ', temp.strip())
#             temp = re.sub(r'[\x91\x92]', '\'', temp)
            resources_lst.append(temp.strip())
    return '; '.join(resources_lst)


def get_timeframe():
    time_frame_index  = [i for i, item in enumerate(home_right_raw_lst) if re.search('Time-frame', item)]
    return home_right_raw_lst[time_frame_index[0]] if len(time_frame_index) == 1 else 'Time-frame: '

def get_countries():
    try:
        countries_index = home_right_raw_lst.index('Countries') + 1
        next_index = home_right_raw_lst.index('Contact information')
        countries = home_right_raw_lst[countries_index:next_index]
        return ",".join(countries)
    except:
        return ''
    
def get_hashtag():
    try:
        return list(filter(tweet_re.match, home_right_raw_lst))[0]
    except:
        return ''

#*****************************************

# SETTING UP VARIABLES
base_url = 'https://sustainabledevelopment.un.org/partnership/?p='

functions = [get_title, get_goals, get_partners, get_description, get_resources, get_timeframe, get_countries, get_hashtag]

ids = open('good_ids.txt').read().split()

# open file
data_file = open('data.csv', 'w')

data_file.write('Project_idx\tTitle\tGoals\tPartners\tDescription\tResources\tTime_frame\tCountries\tHashtag\n')

df_raw = []

# start collecting data
for ide in ids:

    project_idx = '0'*(5 - len(ide)) + ide

    url = base_url + ide
    success_connect = False
    
    while not success_connect:
        try:
            r = requests.get(url)
            success_connect = True
        except requests.exceptions.ConnectionError:
            sleep(1000)

    raw_data = r.text
    
    print(url)
    
    soup = BeautifulSoup(raw_data, 'html.parser')

    home_right = soup.find('div', attrs={'class':'homeRight'})
    
    home_right_raw = str(home_right)

    home_right_raw_lst = home_right.getText().split('\n')
    home_right_raw_lst = list(filter(None, home_right_raw_lst))
    
    row = [f() for f in functions]
    
    row.insert(0, repr(project_idx))
    
    df_raw.append(row)

df = pd.DataFrame(df_raw, columns=['Project_idx', 'Title','Goals', 'Partners', \
                                  'Description', 'Resources', 'Time_frame' ,'Countries', 'Hashtag'] )

writer = pd.ExcelWriter('output.xlsx')
df.to_excel(writer, index=False)
writer.save()




    
data_file.close()
