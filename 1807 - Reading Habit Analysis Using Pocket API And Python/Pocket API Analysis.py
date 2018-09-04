import requests
import pandas as pd
from pandas.io.json import json_normalize
import json
import datetime
import matplotlib.pyplot as plt


# STEP 1: Get a consumer_key by creating a new Pocket application
# Link: https://getpocket.com/developer/apps/new

# STEP 2: Get a request token
# Connect to the Pocket API
# pocket_api variable stores the http response
pocket_api = requests.post('https://getpocket.com/v3/oauth/request',
                           data = {'consumer_key':'12345-23ae05df52291ea13b135dff',
                                   'redirect_uri':'https://google.com'})

# Check the response: if 200, then it means all OK
pocket_api.status_code       

# Check error reason, if any
# print(pocket_api.headers['X-Error'])

# Here is your request_token
# This is a part of the http response stored in pocket_api.text
pocket_api.text

# STEP 3: Authenticate 
# Modify and paste the link below in the browser and authenticate
# Repace text after "?request_token=" with the request_token generated above
# https://getpocket.com/auth/authorize?request_token=PASTE-YOUR-REQUEST-TOKEN-HERE&redirect_uri=https://getpocket.com/connected_applications


# STEP 4: Generate an access_token
# After authenticating in the browser, return here
# Use your consumer_key and request_token below
pocket_auth = requests.post('https://getpocket.com/v3/oauth/authorize',
                            data = {'consumer_key':'12345-23ae05df52291ea13b135dff',
                                    'code':'a1dc2a39-abcd-af28-e235-25ddd4'})

# Check the response: if 200, then it means all OK
# pocket_auth.status_code

# Check error reason, if any
# print(pocket_auth.headers['X-Error'])

# Finally, here is your access_token
# We're done authenticating
pocket_auth.text


# Get data from the API
# Reference: https://getpocket.com/developer/docs/v3/retrieve
pocket_add = requests.post('https://getpocket.com/v3/get',
                           data= {'consumer_key':'12345-23ae05df52291ea13b135dff',
                                  'access_token':'b07ff4be-abcd-4685-2d70-d47816',
                                  'state':'all',
                                  'detailType':'simple'})

# Check the response: if 200, then it means all OK
# pocket_add.status_code

# Here is your fetched JSON data
pocket_add.text


# Prepare the dataframe: convert JSON to table format
json_data = json.loads(pocket_add.text)

df_temp = pd.DataFrame()
df = pd.DataFrame()
for key in json_data['list'].keys():
        df_temp  = pd.DataFrame(json_data['list'][key], index=[0])
        df = pd.concat([df, df_temp])

df = df[['item_id','status','favorite','given_title','given_url','resolved_url','time_added','time_read','time_to_read','word_count']]
df.head(5)

# Clean up the dataset
df.dtypes
df[['status','favorite','word_count']] = df[['status','favorite','word_count']].astype(int)
df['time_added'] = pd.to_datetime(df['time_added'],unit='s')
df['time_read'] = pd.to_datetime(df['time_read'],unit='s')
df['date_added'] = df['time_added'].dt.date
df['date_read'] = df['time_read'].dt.date

# Save the dataframe as CSV locally
df.to_csv('pocket_list.csv')

# Check the data types
df.dtypes


# Answer questions using data

# How many items are there in my Pocket?
print(df['item_id'].count())

# What % of articles are read?
print((df['status'].sum()*100)/df['item_id'].count())

# How long is the average article in my Pocket? (minutes)
df['time_to_read'].describe()

# How long is the average article in my Pocket? (word count)
df['word_count'].describe()

# What is the % of favorites?
print((df['favorite'].sum()*100)/df['item_id'].count())

# How many words have I read till date?
print(df.loc[df['status'] == 1, 'word_count'].sum())

# How many books is this equivalent to?
print(df.loc[df['status'] == 1, 'word_count'].sum()/64000)

# How were the articles added over time?
plot_added = df.groupby('date_added')['item_id'].count()
plot_added.describe()
# plot_added.head(10)

# How were the articles read over time?
plot_read = df.groupby('date_read')['status'].sum()
plot_read.describe()
#plot_read.head(10)

# Wordcloud of the topics I read about
from wordcloud import WordCloud, STOPWORDS

stopwords = set(STOPWORDS)
wordcloud = WordCloud(background_color='white',
                      stopwords=stopwords,
                      max_words=300,
                      max_font_size=40, 
                      random_state=42
                      ).generate(str(df['given_title']))

print(wordcloud)
fig = plt.figure(1)
plt.imshow(wordcloud)
plt.axis('off')
plt.show()
fig.savefig("Pocket Wordcloud.png", dpi=900)