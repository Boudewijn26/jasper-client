# -*- coding: utf-8-*-
import os
import re
from getpass import getpass
import yaml
from pytz import timezone
import feedparser
import client.jasperpath as jasperpath


def run():
    profile = {}

    print("Welcome to the profile populator. If, at any step, you'd prefer " +
          "not to enter the requested information, just hit 'Enter' with a " +
          "blank field to continue.")

    def simple_request(var, cleanVar, cleanInput=None):
        user_input = input(cleanVar + ": ")
        if user_input:
            if cleanInput:
                user_input = cleanInput(user_input)
            profile[var] = user_input

    # name
    simple_request('first_name', 'First name')
    simple_request('last_name', 'Last name')

    # phone number
    def clean_number(s):
        return re.sub(r'[^0-9]', '', s)

    phone_number = clean_number(input("\nPhone number (no country " +
                                          "code). Any dashes or spaces will " +
                                          "be removed for you: "))
    profile['phone_number'] = phone_number

    # carrier
    print("\nPhone carrier (for sending text notifications).")
    print("If you have a US phone number, you can enter one of the " +
          "following: 'AT&T', 'Verizon', 'T-Mobile' (without the quotes). " +
          "If your carrier isn't listed or you have an international " +
          "number, go to http://www.emailtextmessages.com and enter the " +
          "email suffix for your carrier (e.g., for Virgin Mobile, enter " +
          "'vmobl.com'; for T-Mobile Germany, enter 't-d1-sms.de').")
    carrier = input('Carrier: ')
    if carrier == 'AT&T':
        profile['carrier'] = 'txt.att.net'
    elif carrier == 'Verizon':
        profile['carrier'] = 'vtext.com'
    elif carrier == 'T-Mobile':
        profile['carrier'] = 'tmomail.net'
    else:
        profile['carrier'] = carrier

    # location
    def verifyLocation(place):
        feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/' +
                                place)
        numEntries = len(feed['entries'])
        if numEntries == 0:
            return False
        else:
            print("Location saved as " + feed['feed']['description'][33:])
            return True

    print("\nLocation should be a 5-digit US zipcode (e.g., 08544). If you " +
          "are outside the US, insert the name of your nearest big " +
          "town/city.  For weather requests.")
    location = input("Location: ")
    while location and not verifyLocation(location):
        print("Weather not found. Please try another location.")
        location = input("Location: ")
    if location:
        profile['location'] = location

    # timezone
    print("\nPlease enter a timezone from the list located in the TZ* " +
          "column at http://en.wikipedia.org/wiki/" +
          "List_of_tz_database_time_zones, or none at all.")
    tz = input("Timezone: ")
    while tz:
        try:
            timezone(tz)
            profile['timezone'] = tz
            break
        except:
            print("Not a valid timezone. Try again.")
            tz = input("Timezone: ")

    response = input("\nWould you prefer to have notifications sent by " +
                         "email (E) or text message (T)? ")
    while not response or (response != 'E' and response != 'T'):
        response = input("Please choose email (E) or text message (T): ")
    profile['prefers_email'] = (response == 'E')

    stt_engines = {
        "sphinx": None,
        "google": "GOOGLE_SPEECH"
    }

    response = input(('\nIf you would like to choose a specific STT ' +
                     'engine, please specify which.\nAvailable ' +
                     'implementations: {0}. (Press Enter to default ' +
                     'to PocketSphinx): ').format(stt_engines.keys()))
    if (response in stt_engines):
        profile["stt_engine"] = response
        api_key_name = stt_engines[response]
        if api_key_name:
            key = input("\nPlease enter your API key: ")
            profile["keys"] = {api_key_name: key}
    else:
        print("Unrecognized STT engine. Available implementations: %s"
              % stt_engines.keys())
        profile["stt_engine"] = "sphinx"

    # write to profile
    print("Writing to profile...")
    if not os.path.exists(jasperpath.CONFIG_PATH):
        os.makedirs(jasperpath.CONFIG_PATH)
    outputFile = open(jasperpath.config("profile.yml"), "w")
    yaml.dump(profile, outputFile, default_flow_style=False)
    print("Done.")

if __name__ == "__main__":
    run()
