import requests
import requests.auth
import json
import os
import configparser
from PIL import Image

# Credentials and Secrets
# https://docs.python.org/3/library/configparser.html
config = configparser.ConfigParser()
config.read('../../credentials.ini')
username = config['REDDIT']['username']
password = config['REDDIT']['password']
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
pc_username = config['DEFAULT']['pc_username']

# App Settings
appname = "wallpaper"
version = "0.1"
user_agent = "{}/{} by {}".format(appname, version, username)
base_url = "https://oauth.reddit.com"
download_folder = "C:\\Users\\{}\\Pictures\\WorthyBackgrounds\\".format(pc_username)

# Get Token
def GetToken():
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {"grant_type": "password", "username": username, "password": password}
    headers = {"User-Agent": user_agent}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    data = response.json()
    token = data["access_token"] 
    print("Authentication Successful: {}\n".format(token))

    return token

# Verify Files
def VerifyFiles(files):
    print("Verifying...")
    for file in files:
        # Remove file if verification throws exception
        try:
            im = Image.open(file)
            im.verify()
        except:
            os.remove(file)
            print("Removing:", file)
    print("\n")

# Get Images From Subreddit 
def GetImagesFromSubreddit(subreddit, timeFilter, token):
    try:
        headers = {"Authorization": "bearer " + token, "User-Agent": user_agent}
        response = requests.get("{}/r/{}{}".format(base_url, subreddit, timeFilter), headers=headers)
        data = response.json()

        files = []
        
        for listing in data["data"]["children"]:
            # Get the needed key values
            # Skip listing if all keys are not found
            try:
                values = {
                    "url": listing["data"]["url"],
                    "title": listing["data"]["title"],
                    "width": listing["data"]["preview"]["images"][0]["source"]["width"],
                    "height": listing["data"]["preview"]["images"][0]["source"]["height"]
                }
            except:
                print("\tinvalid keys")
                continue
            
            #Get Extension
            extension = ".png"
            if ".jpg" in values["url"]:
                extension = ".jpg"

            # Get Title
            # Filter out unwanted filename characters
            imageFile = values["title"]
            bad_chars = [';', ':', '!', "*", ".", " ", "~", "#", "%", "&", "{", "}", "\\", "?", "/", "+", "|", '"']
            for i in bad_chars: 
                imageFile = imageFile.replace(i, '') 

            # Get Image Size (filter out unwanted aspect ratios)
            # Catch error if these keys don't exists
            w = values["width"]
            h = values["height"]
            if (w/h) > 1.2:
                # Save Image
                fullImagePath = "{}{}{}".format(download_folder, imageFile, extension)
                with open(fullImagePath, 'wb') as f:
                    f.write(requests.get(values["url"]).content)
                    files.append(fullImagePath)

        VerifyFiles(files)
    except:
        print("Error getting images for: {}".format(subreddit))

# Imaginary Network
# https://www.reddit.com/r/ImaginaryNetwork/wiki/networksublist
timeFilter = "/top/?t=week"
subreddits = [
    # Landscapes
    "ImaginaryWorlds",
    "ImaginaryMindscapes",
    "ImaginaryWastelands",
    "ImaginaryHellscapes",
    "ImaginaryWildlands",
    "ImaginaryBattlefields",
    "ImaginaryBodyscapes",
    "ImaginaryCityscapes",

    # Characters
    "ImaginaryWarriors",
    "ImaginaryWizards",
    "ImaginaryKnights",

    # Architecture

    # Monsters
    "ImaginaryDragons",

    # Technology
    "ImaginaryCyberpunk",
    "ImaginarySteampunk",

    # Wallpaper
    "wallpaper"
]

# Run Script
token = GetToken()
for subreddit in subreddits:
    print(subreddit)
    GetImagesFromSubreddit(subreddit, timeFilter, token)

