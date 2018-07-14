# Identifying Forced And Fake Twitter Trends
# CREATED BY: Ayush Kumar
# WEBSITE: https://everydayplots.com
# GITHUB: https://github.com/kumaagx

# Description: Input any Twitter trend or search term and see if it is trending naturally or
# being forced to trend. A genuine trend should have a variety of unique tweets distributed over time, 
# however, a forced or fake trend has a lot of unevenly distributed duplicate tweets due to people / bots 
# directly copy-pasting from pre-created templates in bulk.

# Features:
# 1. Check the currently trending topics within R
# 2. Extract & clean-up original tweets for trends / search terms
# 3. Visualize the tweet frequency for a trend over time
# 4. Analyze for duplicity / fakeness and assign a score

# --------------------- #
# INITIALIZE
# --------------------- #

setwd('C:/Analysis Folder')

# Load the required R libraries
# install.packages("twitteR")
library(twitteR)
library(stringr)

download.file(url="http://curl.haxx.se/ca/cacert.pem",destfile="cacert.pem")

# Set constant requestURL
requestURL <- "https://api.twitter.com/oauth/request_token"
# Set constant accessURL
accessURL <- "https://api.twitter.com/oauth/access_token"
# Set constant authURL
authURL <- "https://api.twitter.com/oauth/authorize"

# Get your keys from https://apps.twitter.com/
consumerKey <- "XXXXX"
consumerSecret <- "XXXXX"
accessToken <- "XXXXX"
accessTokenSecret <- "XXXXX"

setup_twitter_oauth(consumerKey,
                    consumerSecret,
                    accessToken,
                    accessTokenSecret)

# --------------------- #
# PART 1 - SEARCH AVAILABLE TRENDS
# --------------------- #

# Search for trending topics

woeid = availableTrendLocations()
woeid[woeid$country == 'India',]

tr <- getTrends(23424848) # Trends in India
tr[,1]

# --------------------- #
# PART 2 - DEFINE FUNCTION
# --------------------- #

IdentifyFakeTrend <- function(trend) {
  
  # twitteR docuentation: https://www.rdocumentation.org/packages/twitteR/versions/1.1.9
  #twi1 <- searchTwitter("#SampleHashtag" ,n=9000,lang=NULL, resultType="recent")
  twi_all <- searchTwitter(trend, n=10000, lang=NULL, since='2018-05-01') # Extract tweets for a trend
  twi_ori <- strip_retweets(twi_all) # Keep only "pure" original tweets
  
  twi_all_df <- twListToDF(twi_all) # Convert tweet list to dataframe
  twi_ori_df <- twListToDF(twi_ori) # Convert tweet list to dataframe
  print(paste("Total tweets about",trend, "are:",nrow(twi_all_df),"( Tweets -",nrow(twi_ori_df),"| RTs -",nrow(twi_all_df)-nrow(twi_ori_df),")",sep = " "))
  
  # Insert freq plot here, include retweets in it
  freqplot <- subset(twi_ori_df, select = c("created", "id"))
  timest <- as.POSIXct(freqplot$created)
  attributes(timest)$tzone <- "Asia/Calcutta"
  brks <- trunc(range(timest), "mins")
  hist(timest, freq = TRUE, breaks=seq(brks[1], brks[2]+3600, by="5 min"), main = paste("Pattern of tweets on ", trend), xlab = "Time")

  # Extract essential columns: text, created, id, screenName
  twi_clean <- subset(twi_ori_df, select = c("text", "created", "id", "screenName"))
  
  # Clean-up the tweet text
  twi_clean$text <- gsub("[^[:alnum:][:space:]]*","", twi_clean$text)
  twi_clean$text <- gsub("http\\w*","", twi_clean$text)
  twi_clean$text <- gsub("\\n"," ", twi_clean$text)
  twi_clean$text <- gsub("\\s+", " ", str_trim(twi_clean$text))
  twi_clean$text <- tolower(twi_clean$text)

  # Create a sorted table of unique tweets w/ count
  twfreq <- as.data.frame(table(twi_clean$text)) # create a freq table of duplicates
  twfreq <- twfreq[!(twfreq$Var1==""),] # remove blanks
  twfreq <- twfreq[order(-twfreq$Freq),] # sort by frequency of duplicates
  # print(head(twfreq))
  
  # Calculate tweet uniqueness score
  # count unique tweets / count total tweets
  # uniqueness score of natural trends is closer to 1
  # uniqueness score of fake / forced trends is closer to 0
  uniqueness = nrow(twfreq[2])/sum(twfreq[2])
  
  # For verifying manually
  # write.csv(twi3, file = "twi3.csv")
  # write.csv(twfreq, file = "twfreq.csv")
  
  #print(uniqueness)
  print(paste("The uniqueness score is ",uniqueness))

  return(twfreq)
}

# --------------------- #
# PART 3 - TEST THE FUNCTION
# --------------------- #

twfreq = IdentifyFakeTrend('#SampleHashtag')
twfreq = IdentifyFakeTrend('#MondayMotivation')