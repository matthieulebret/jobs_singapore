import streamlit as st
import pandas as pd
import numpy as np
import json
import urllib.parse
import requests
from selenium import webdriver

import plotly.graph_objects as go

import altair as alt

import math
import re

import time
import random

import xlrd

import plotly.express as px


from bs4 import BeautifulSoup

st.set_page_config('Job market analysis',layout='wide')

st.title("Job market analysis - Singapore")

st.image('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixid=MXwxMjA3fDB8MHxzZWFyY2h8MXx8d29ya2luZ3xlbnwwfHwwfA%3D%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=60')


# driver = webdriver.Chrome()
#
# biglist = []
# errorlist = []
#
# placeholder = st.empty()
# progholder = st.empty()
# mybar = st.progress(0)
#
# for page in range(19):
#
#     base_url = 'https://www.efinancialcareers.sg/search/?location=Singapore&latitude=1.352083&longitude=103.819836&countryCode=SG&locationPrecision=Country&radius=40&radiusUnit=km&page='+str(page)+'&pageSize=100&currencyCode=SGD&language=en'
#
#     try:
#         driver.get(base_url)
#         time.sleep(10)
#         divcards = driver.find_elements_by_class_name('search-card')
#         jobtitles = [div.text for div in divcards]
#         biglist.extend(jobtitles)
#     except:
#         errorlist.append(page)
#
#     with placeholder:
#         st.write('File #{0} complete '.format(page)+'/ '+str(19)+'. '+str(len(errorlist))+' errors so far.')
#     with progholder:
#         pct_complete = '{:,.2%}'.format(page/19)
#         st.write(pct_complete,' complete.' )
#         mybar.progress(min(page/19,1))
#
#     time.sleep(5)

# joblinks = [div.find_element_by_xpath("//a[contains(@href,'job')]").get_attribute('href') for div in divcards]
# card_companies = [div.find_element_by_class_name('card-company') for div in divcards]
#
# companieslist = [card.find_element_by_xpath("//span[contains(@class,'margin-right-5 ng-star-inserted')]") for card in card_companies]
# locationslist = [card.find_element_by_xpath("//span[contains(@id,'searchResultLocation')]") for card in card_companies]
# companies = [company.text for company in companieslist]
# locations = [location.text for location in locationslist]

# driver.close()

# jobtitles = biglist
#
# df = pd.DataFrame([jobtitles]).transpose()

# df.to_csv('adlist.csv')

# df.to_csv('adlist.csv')
df = pd.read_csv('adlist.csv').iloc[:,1:]
df.columns = ['Ad']


def gettitle(string):
    return string.splitlines()[0]
def getcomp(string):
    return string.splitlines()[2]
def getdesc(string):
    return string.splitlines()[3]+' '+string.splitlines()[4]
def getsal(string):
    return string.splitlines()[-1]
def getdate(string):
    return string.splitlines()[-3]
def getcontract(string):
    return string.splitlines()[-4]


df['Job Title'] = df['Ad'].apply(gettitle)
df['Company'] = df['Ad'].apply(getcomp)
df['Job Desc'] = df['Ad'].apply(getdesc)
df['Salary'] = df['Ad'].apply(getsal)
df['Posted'] = df['Ad'].apply(getdate)
df['Contract'] = df['Ad'].apply(getcontract)
df['Location'] = 'Singapore'

df = df.iloc[:,1:]
df = df.drop_duplicates('Job Desc')

with st.beta_expander('View all jobs'):
    st.write(df)

dfana = df

### Analysis ###

groupdf = df.groupby('Company')['Job Desc'].count().sort_values(ascending=False)

groupdf = pd.DataFrame(groupdf)
totaljobs = groupdf['Job Desc'].sum()

groupdf['Share of Total'] = groupdf['Job Desc']/totaljobs

st.header('Top ad publishers')

formatdf = groupdf.style.format({"Share of Total":'{:,.2%}'})

st.write(formatdf)

df = groupdf.head(10)
df.reset_index(inplace=True)


fig = alt.Chart(df).mark_bar().encode(alt.X('Company:N',sort='-y'),y='Job Desc',color=alt.Color('Company:N',legend=None)).properties(height=500)
st.altair_chart(fig,use_container_width=True)


nbfulltime = dfana[dfana['Contract']=='Full time'].count()[0]/totaljobs

def hasNumbers(string):
    return any(char.isdigit() for char in string)

dfana['Salary detail'] = dfana['Salary'].apply(hasNumbers)

nbsalary = dfana['Salary detail'].sum()/totaljobs

def hasvp(string):
    listtitles = ['vp','VP','vice president','vice-president','Vice','Director','director']
    excludewords = ['Assistant','AVP']
    returnlist = [title in string for title in listtitles]
    excludelist = [word in string for word in excludewords]

    if True in returnlist and True not in excludelist:
        return 1


dfana['Big Title'] = dfana['Job Title'].apply(hasvp)


nbvp = dfana['Big Title'].sum()/totaljobs

st.write('Percentage of full time positions: ',str('{:,.2%}'.format(nbfulltime)))
st.write('Percentage of positions with some salary information: ',str('{:,.2%}'.format(nbsalary)))
st.write('Percentage of positions with salary = competitive or vague: ',str('{:,.2%}'.format(1-nbsalary)))
st.write('Percentage of positions with VP or Director title: ',str('{:,.2%}'.format(nbvp)))

st.header('List of jobs for VP and Director')

dfana = dfana[dfana['Big Title']==1].iloc[:,:-2]

companylist = dfana['Company'].sort_values(ascending=True).unique().tolist()
companylist.insert(0,'All')

selectcompany = st.selectbox('Filter by company',companylist)

if selectcompany != 'All':
    dfana =dfana[dfana['Company']==selectcompany]

st.table(dfana)
