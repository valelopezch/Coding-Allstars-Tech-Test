import streamlit as st
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from datetime import date
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import time
import os

#### Auxiliar Functions ####

# @st.cache
def get_title(soup):
    title1 = soup.find('h1', class_='banner-title m-b-0')
    if title1:
        return title1.get_text()
    else:
        title2 = soup.find('h1', class_='cds-119 css-1shw822 cds-121')
        if title2:  
            return title2.get_text()
    return None

def get_cat(soup):
    categories = []
    cats1 = soup.find_all('a', class_='_172v19u6 color-white font-weight-bold')
    if cats1:
        for cat in cats1:
            categories.append(cat.get_text())
        return categories[1]
    else:
        cats2 = soup.find_all('li', class_='css-cxisig')
        if cats2:
            for cat in cats2:
                categories.append(cat.get_text())
            return categories[1]
    return None


def get_instructor(soup):
    inst1 = soup.find('div', class_='_1qfi0x77 instructor-count-display')
    if inst1:
        res = inst1.get_text().split()[:2]
        instructor = " ".join(res)
        return instructor
    else:
        inst2 = soup.find('a', class_='css-1a0pimv')
        if inst2:
            res = inst2.get_text().split()[:2]
            instructor = " ".join(res)
            return instructor
    return None


def get_description(soup):
    des1 = soup.find('p', class_='max-text-width m-b-0')
    if des1:
        return des1.get_text()
    else:
        des2 = soup.find('p', class_='cds-119 css-n1ma14 cds-121')
        if des2:
            return des2.get_text()
    return None

def get_rating(soup):
    rat1 = soup.find('div', class_='_wmgtrl9 color-white ratings-count-expertise-style')
    if rat1:
        rat = rat1.get_text().split()[0]
        return rat
    else:
        rat2 = soup.find('div', class_='css-oj3vzs')
        if rat2:
            rat = rat2.get_text().split()[0]
            return rat
    return None

def get_students(soup):
    students1 = soup.find('div', class_='_1fpiay2')
    if students1:
        s = students1.get_text().split()[0]
        return s
    else:
        students2 = soup.find('div', class_='css-oj3vzs')
        if students2:
            s = students2.get_text().split()[2]
            return s
    return None

def get_info(course_url):
    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Chrome(options=options)

    browser.get(course_url)
    browser.implicitly_wait(1)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    browser.quit()
    if soup is None:
        print("Page not found")
    else:
        title = get_title(soup)
        cat = get_cat(soup)
        des = get_description(soup)
        rat = get_rating(soup)
        students = get_students(soup)
        instructor = get_instructor(soup)

        return cat, title, instructor, des, students, rat

def get_links(soup):
    links = []
    c_link = soup.find_all('a')

    for c in c_link:
        links.append('https://coursera.org' + str(c['href']))
    return links

def get_df(cat_name):
    cat_name = cat_name.lower()
    cat_name = cat_name.replace(' ', '-')

    course_category = []
    course_name = []
    course_instructor =[]
    course_description = []
    course_students_enrolled = []
    course_ratings = []

    url_page = 'https://www.coursera.org/search?query=' + cat_name + '&page=' + str(1) + '&index=prod_all_launched_products_term_optimization'
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    driver.get(url_page)
        
    driver.implicitly_wait(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    links = get_links(soup)
    for l in links[12:30]:
        info = get_info(l)
        if None not in info:
            course_category.append(info[0])
            course_name.append(info[1])
            course_instructor.append(info[2])
            course_description.append(info[3])
            course_students_enrolled.append(info[4])
            course_ratings.append(info[5])

    coursera_df = pd.DataFrame.from_dict({'Course Category': course_category,
                            'Course Name': course_name,
                            'Course Instructor': course_instructor,
                            'Course Description' : course_description,
                            'Number of students': course_students_enrolled,
                            'Number of ratings': course_ratings}, orient='index')
    coursera_df = coursera_df.transpose()
    return coursera_df.to_csv().encode('utf-8')

#### End of Auxiliary Functions ####

##############################################################################################################################################
### Website

st.set_page_config(page_title = 'My webpage', page_icon = ':chart:', layout = 'wide')

# Header section

with st.container():
    st.title('Coursera Courses Information')
    st.subheader('Hi :wave:, in this website you can find the courses you are looking for.')
    st.write('With the purpose of helping users find courses much easier and filtered by category!')
    st.write('For more detailed information: ','[Go to Coursera](https://www.coursera.org/)')

# body

with st.container():
    st.write('---')
    option = st.selectbox('Select your category:',
    ('','Data Science', 'Business', 'Computer Science', 'Health', 'Social Sciences', 'Personal Development', 'Art and Humanities', 'Physical Science and Engineering', 'Language Learning', 'Information Tecnology', 'Math and Logic'))
    if option != '':
        st.write('You selected: ', option)
        st.write('Errors may occur due to connection problems, if so please reload the website.')
        st.write('---')
        df = get_df(option)
        d = st.download_button(label = 'Download CVS file', data = df, file_name = str(option).replace(' ', '') + '.csv')
        if d:
            st.write('After downloading the file reload the website.')
        
        
        

    
