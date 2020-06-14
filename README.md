

# SETUP

## Twitter config

Copy sample_config.py to config.py and add your consumer key, consumer secret, access key, and access secret

## Python3.7 setup
pip install tqdm, tweepy


## Usage
python main.py -h # for help
python main.py 100 # 100 is the number of users you send tweet to
python main.py 100 --forreals # you need this flag to send the DM's for reals
python main.py 100 --update # to update your local db of followers
