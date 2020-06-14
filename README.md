

# SETUP

## Twitter config

Copy sample_config.py to config.py and add your consumer key, consumer secret, access key, and access secret

## Python3.7 setup
pip install tqdm, tweepy, geocode


## Example Usage

Populate your follower database locally like below
`python main.py --populate`
Ideally you wont do this very often, maybe monthly once

Use the dm flag and additional filters to filter your users
and direct message them
To DM the top 10 followers who has the most no of followers
`python main.py --dm`

To DM the top 1000 followers who has the most no of followers
`python main.py --dm --limit 1000`

To DM all the users who are from US, active in the last 30 days 
and the top 100 users with the most no of followers
`python main.py --dm --cc us --days 30 --limit 100`
  