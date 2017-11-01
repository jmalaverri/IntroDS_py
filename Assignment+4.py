
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[39]:

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy import stats
get_ipython().magic('pinfo stats.ttest_ind')


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[3]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 
          'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 
          'NH': 'New Hampshire', 
          'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[4]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    
    #Open the file
    fname = 'university_towns.txt'
    fh = open(fname).readlines()
    
    sorted(states.values())
    #Preparing the data
    #1 Replace name state by two letter acronyms
    data = []
    for line in fh:
        if '[edit]' in line:
            if line.split('[edit]')[0] in states.values():
                for key, value in states.items():
                    if line.split('[edit]')[0] == value:
                        data.append(key)
        else:
            data.append(line)
    
    #2. For "RegionName", when applicable, removing every character from " (" to the end.
    data = [ item.split(' (')[0] if ' (' in item else item for item in data ]
    #3. Depending on how you read the data, you may need to remove newline character '\n'.
    data = [ line.split('\n')[0] if '\n' in line else line for line in data ]
    
    tmp = []
    for key, name in states.items():
        if key not in data: continue
        i = data.index(key)
        i = i + 1
        while ( ( i < len(data) ) & ( data[i] not in states.keys() )  ):
                tmp.append({"State": name, "RegionName": data[i]})
                #print('state {}, RegionName {}'.format(key, data[i]))
                i = i + 1
                if (i == len(data)): break

    df = pd.DataFrame(tmp, columns=["State", 'RegionName'])
    
    return df.sort(['State'], ascending=True)

get_list_of_university_towns()


# In[5]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdplev = pd.read_excel(open('gdplev.xls', 'rb'), sheetname=0, skiprows = 5, convert_float=True)
    #Cleaning and organizing the data
    columns_to_keep = ['GDP in billions of chained 2009 dollars.1', 'Unnamed: 4']
    gdplev = gdplev[columns_to_keep]
    gdplev = gdplev.rename(index = str, columns = {'GDP in billions of chained 2009 dollars.1':'GDP chained 2009',
                                                  'Unnamed: 4':'Quarter'})
    gdplev = gdplev[ gdplev['Quarter'] >= '2000q1' ]
    #A recession is defined as starting with two consecutive quarters 
    #of GDP decline, and ending with two consecutive quarters of GDP growth.
    
    gdplev['diff'] = gdplev['GDP chained 2009'].diff()
    #Take rows where values from diff is finite:
    gdplev = gdplev[np.isfinite(gdplev['diff'])]
    gdplev['Inc_Dec'] = [ 1 if x > 0 else 0 for x in gdplev['diff'] ]
 
    #Find the pattern 0..0011, i.e., decline...,decline...increase,increase...
    gdp_b = pd.Series( gdplev['Inc_Dec'])
    
    #Tip from coursera forum
    prev = -1
    seq = []
    for ind, v in zip(gdp_b.index, gdp_b.values):
        if v == 0:
            if prev == 1 and len(seq) <= 1:
                seq = []
            seq.append(ind)
        elif v == 1:
            if len(seq) >= 2:
                seq.append(ind)
                if prev == 1:
                    break
            else:
                seq = []
        prev = v

    return gdplev['Quarter'][seq[0]]

get_recession_start()


# In[7]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    gdplev = pd.read_excel(open('gdplev.xls', 'rb'), sheetname=0, skiprows = 5, convert_float=True)
    #Cleaning and organizing the data
    columns_to_keep = ['GDP in billions of chained 2009 dollars.1', 'Unnamed: 4']
    gdplev = gdplev[columns_to_keep]
    gdplev = gdplev.rename(index = str, columns = {'GDP in billions of chained 2009 dollars.1':'GDP chained 2009',
                                                  'Unnamed: 4':'Quarter'})
    gdplev = gdplev[ gdplev['Quarter'] >= '2000q1' ]
    #A recession is defined as starting with two consecutive quarters 
    #of GDP decline, and ending with two consecutive quarters of GDP growth.
    
    gdplev['diff'] = gdplev['GDP chained 2009'].diff()
    #Take rows where values from diff is finite:
    gdplev = gdplev[np.isfinite(gdplev['diff'])]
    gdplev['Inc_Dec'] = [ 1 if x > 0 else 0 for x in gdplev['diff'] ]
 
    #Find the pattern 0..0011, i.e., decline...,decline...increase,increase...
    gdp_b = pd.Series( gdplev['Inc_Dec'])
    
    #Tip from coursera forum
    prev = -1
    seq = []
    for ind, v in zip(gdp_b.index, gdp_b.values):
        if v == 0:
            if prev == 1 and len(seq) <= 1:
                seq = []
            seq.append(ind)
        elif v == 1:
            if len(seq) >= 2:
                seq.append(ind)
                if prev == 1:
                    break
            else:
                seq = []
        prev = v

    return gdplev['Quarter'][seq[-1]]
get_recession_end()


# In[9]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    #A recession bottom is the quarter within a recession which had the lowest GDP.
    
    gdplev = pd.read_excel(open('gdplev.xls', 'rb'), sheetname=0, skiprows = 5, convert_float=True)
    #Cleaning and organizing the data
    columns_to_keep = ['GDP in billions of chained 2009 dollars.1', 'Unnamed: 4']
    gdplev = gdplev[columns_to_keep]
    gdplev = gdplev.rename(index = int, columns = {'GDP in billions of chained 2009 dollars.1':'GDP chained 2009',
                                                  'Unnamed: 4':'Quarter'})
    gdplev = gdplev[ gdplev['Quarter'] >= '2000q1' ]
        
    gdplev = gdplev[lambda df1: (gdplev['Quarter'] >= get_recession_start()) & (gdplev['Quarter'] <= get_recession_end())]
            
    return gdplev.loc[lambda df: df['GDP chained 2009'].idxmin(), 'Quarter']
get_recession_bottom()


# In[11]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    housing_data = pd.read_csv('City_Zhvi_AllHomes.csv')
    
    count_quarter = 0
    quarter = 1
    list_col_names = []
    
    #Converting housing_data to quarter and calculating the mean
    for col_name in housing_data.loc[:, '2000-01':].columns:
        count_quarter = count_quarter + 1
        list_col_names.append(col_name) 
        
        if (count_quarter == 3):
            col = col_name.split('-')[0]
            count_quarter = 0
                        
            quarter_of_year = housing_data.loc[:,list_col_names[0]:list_col_names[-1]]
            housing_data['{0}q{1}'.format(col, quarter)] = quarter_of_year.mean(axis = 1)
            
            quarter = quarter + 1                      
            list_col_names = []
        
        if (col_name.split('-')[0] == '2016' and col_name.split('-')[1] == '07'):            
            quarter_of_year = housing_data.loc[:,'2016-07':'2016-08']
            housing_data['{0}q{1}'.format('2016', 3)] = quarter_of_year.mean(axis = 1)
            
        if (quarter > 4):
            quarter = 1
    
    #Setting the multindex in the shape of ["State","RegionName"].
    housing_data['State'] = housing_data['State'].apply(lambda x: states[x])  
    housing_data = housing_data.set_index(['State','RegionName']) 
    
    #Just leaving the columns 2000q1 through 2016q3:
    housing_data.drop(housing_data.columns[housing_data.columns.get_loc('1996-04'): housing_data.columns.get_loc('2000q1')], axis=1, inplace=True)
    housing_data.drop(housing_data.columns[housing_data.columns.get_loc('RegionID'): housing_data.columns.get_loc('2000q1')], axis=1, inplace=True)
    
    return housing_data
convert_housing_data_to_quarters()


# In[89]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #Preparing the data
    housing_data = convert_housing_data_to_quarters()    
          
    housing_data['Price Ratio'] = housing_data[get_recession_start()].div(housing_data[get_recession_bottom()])
    
    university_towns = get_list_of_university_towns()
    university_towns = university_towns.set_index(['State', 'RegionName'])
    
    #Clean data from column Price Ratio of university town
    university_town = housing_data.loc[list(university_towns.index)]['Price Ratio'].dropna()
    
    #Computing what are not univeristy towns
    not_university_town_index = set(housing_data.index) - set(university_town.index)
    not_university_town = housing_data.loc[list(not_university_town_index),:]['Price Ratio'].dropna()
   
    #Computing the ttest
    #statistic, pValue = tuple(stats.ttest_ind(university_town, not_university_town)) #other way
    output_ttest = stats.ttest_ind(university_town, not_university_town)
    pValue = output_ttest[1]
    
    if pValue < 0.01:
        different = True
    else:
        different = False
    
    better = [ 'university town' if university_town.mean() < not_university_town.mean() else "non-university town" ]
        
    run_ttest_output = (different, pValue, better[0])
    
    return run_ttest_output
run_ttest()


# In[ ]:



