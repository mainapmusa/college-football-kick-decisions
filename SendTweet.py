import tweepy
import json
import logging

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('./live_game_logs/logs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg["consumer_key"], cfg["consumer_secret"])
    auth.set_access_token(cfg["access_token"], cfg["access_token_secret"])
    return tweepy.API(auth)

def tweet(message, imagePath = ""):

    # Fill in the values noted in previous step here
    cfg = json.load(open("../configs/cfg.json"))

    api = get_api(cfg)
    #270 used since about 10 new lines in typical message I tweet
    while(len(message) > 270):
        logger.info("Tweet contains too many characters: "+len(message))
        message = message[::-1].split('#',1)[1][::-1]
        logger.info("Tweet shortened to: ")
        logger.info(message)

    if imagePath == "":
        api.update_status(status=message)
    else:
        api.update_with_media(imagePath,message)
