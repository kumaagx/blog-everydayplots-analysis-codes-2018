from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime


driver = webdriver.Chrome()

# Extract description of a post from Instagram link
driver.get('https://www.instagram.com/p/BiRnjDsFKzl/')
soup = BeautifulSoup(driver.page_source,"lxml")
desc = " "

for item in soup.findAll('a'):
    desc= desc + " " + str(item.string)

# Extract tag list from Instagram post description
taglist = desc.split()
taglist = [x for x in taglist if x.startswith('#')]
index = 0
while index < len(taglist):
    taglist[index] = taglist[index].strip('#')
    index += 1

# (OR) Copy-paste your tag list manually here
#taglist = ['art', 'instaart', 'iblackwork']

print(taglist)


# Define dataframe to store hashtag information
tag_df  = pd.DataFrame(columns = ['Hashtag', 'Number of Posts', 'Posting Freq (mins)'])

# Loop over each hashtag to extract information
for tag in taglist:
    
    driver.get('https://www.instagram.com/explore/tags/'+str(tag))
    soup = BeautifulSoup(driver.page_source,"lxml")
    
    # Extract current hashtag name
    tagname = tag
    # Extract total number of posts in this hashtag
    # NOTE: Class name may change in the website code
    # Get the latest class name by inspecting web code
    nposts = soup.find('span', {'class': 'g47SY'}).text
        
    # Extract all post links from 'explore tags' page
    # Needed to extract post frequency of recent posts
    myli = []
    for a in soup.find_all('a', href=True):
        myli.append(a['href'])

    # Keep link of only 1st and 9th most recent post 
    newmyli = [x for x in myli if x.startswith('/p/')]
    del newmyli[:9]
    del newmyli[9:]
    del newmyli[1:8]

    timediff = []

    # Extract the posting time of 1st and 9th most recent post for a tag
    for j in range(len(newmyli)):
        driver.get('https://www.instagram.com'+str(newmyli[j]))
        soup = BeautifulSoup(driver.page_source,"lxml")

        for i in soup.findAll('time'):
            if i.has_attr('datetime'):
                timediff.append(i['datetime'])
                #print(i['datetime'])

    # Calculate time difference between posts
    # For obtaining posting frequency
    datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
    diff = datetime.datetime.strptime(timediff[0], datetimeFormat)\
        - datetime.datetime.strptime(timediff[1], datetimeFormat)
    pfreq= int(diff.total_seconds()/(9*60))
    
    # Add hashtag info to dataframe
    tag_df.loc[len(tag_df)] = [tagname, nposts, pfreq]
        
driver.quit()

# Check the final dataframe
print(tag_df)

# CSV output for hashtag analysis
tag_df.to_csv('hashtag_list.csv')