import tweepy
import json

def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg["consumer_key"], cfg["consumer_secret"])
    auth.set_access_token(cfg["access_token"], cfg["access_token_secret"])
    return tweepy.API(auth)

def tweet(message, imagePath = ""):

    # Fill in the values noted in previous step here
    cfg = json.load(open("../configs/cfg.json"))

    api = get_api(cfg)
    #tweet = message
    if imagePath == "":
        api.update_status(status=message)
    else:
        api.update_with_media(imagePath,message)
