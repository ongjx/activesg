from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import telebot

import time
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


def getVenues(browser):
    # select badminton as activity choice
    browser.find_element("id", "activity_filter_chosen").click()
    browser.find_elements("class name", "active-result")[1].click()
    time.sleep(1)
    # Find venues that are sport hall and not school
    venue_select_element = browser.find_element("name", "venue_filter")

    # return [(x.get_attribute("innerText"), x.get_attribute("value")) for x in venue_select_element.find_elements("tag name", "option") if 'sport hall' in x.get_attribute('innerText').lower() and notSchool(x.get_attribute('innerText').lower())]
    return [(x.get_attribute("innerText"), x.get_attribute("value")) for x in venue_select_element.find_elements("tag name", "option")]


def notSchool(venue):
    keywords = ['junior','college','secondary','primary','school']
    for w in keywords:
        if w in venue:
            return False
    return True

def getEpochTimestamp(x):
    return int(datetime.strptime(str(datetime.now().date() + timedelta(days=x)), '%Y-%m-%d').timestamp())

def get_hall_slots(message):
    request = message.text.split()
    if request[0] == "/getslots" and len(request) == 2 and request[1].isdigit():
        return True
    return False

def get_all_slots():
    venues = getVenues(browser)

    # Gather data for next 5 days
    nextFiveDaysEpoch = [getEpochTimestamp(x) for x in range(1,6)]

    for h_name,hid in venues:
        for epochTime in nextFiveDaysEpoch:
            date = datetime.fromtimestamp(epochTime).strftime('%d-%m-%Y')
            url = f"https://members.myactivesg.com/facilities/view/activity/18/venue/{hid}?time_from={epochTime}" # 18 here is badminton activity_id
            browser.get(url)

            available_courts = browser.find_elements("css selector", ".timeslot-container .subvenue-slot input[name='timeslots[]']")
            if len(available_courts) == 0:
                print(f"{h_name} has no available courts on {date}")
            else:
                print(f"{h_name}:")
                for court in available_courts:
                    data = court.get_attribute('value').split(';')
                    print(f"Available Court: {data[0]} @ {date} {data[3]} - {data[4]}")

            randomRestTime = random.randint(5,15)
            time.sleep(randomRestTime)


load_dotenv()
browser = webdriver.Chrome()
venues = None
bot = telebot.TeleBot(os.getenv("API_KEY"))

# navigate to login page
browser.get("https://members.myactivesg.com/auth")

browser.find_element("id", "email").send_keys(os.getenv('username'))
browser.find_element("id", "password").send_keys(os.getenv('password'))
browser.find_element("id", "btn-submit-login").click()
time.sleep(2)

# navigate to booking page
browser.get("https://members.myactivesg.com/bookfacility")


@bot.message_handler(commands=["halls"])
def getHalls(message):
    bot.reply_to(message, 'Retrieving all available sports halls...')
    global venues
    venues = venues or getVenues(browser)
    reply = ""
    for name,id in venues:
        if len(reply + f"{id}: {name}\n") >= 4096:
            bot.send_message(message.chat.id, reply)
            reply = f"{id}: {name}\n"
        else:
            reply += f"{id}: {name}\n"
    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=get_hall_slots)
def get_slots_for_hall(message):
    nextFiveDaysEpoch = [getEpochTimestamp(x) for x in range(1,6)]
    hid = message.text.split()[1]
    global venues
    venues = venues or getVenues(browser)

    result = [i[0] for i in venues if i[1] == hid]
    if len(result) == 0:
        bot.reply_to(message, "Hey there! You have entered an invalid venue id!")
    else:
        bot.send_message(message.chat.id, "Retrieving available slots for the next 5 days...")
        h_name = result[0]
        reply = ""
        for epochTime in nextFiveDaysEpoch:
            date = datetime.fromtimestamp(epochTime).strftime('%A %d-%m-%Y')
            url = f"https://members.myactivesg.com/facilities/view/activity/18/venue/{hid}?time_from={epochTime}" # 18 here is badminton activity_id
            browser.get(url)
            available_courts = browser.find_elements("css selector", ".timeslot-container .subvenue-slot input[name='timeslots[]']")
            if len(available_courts) != 0:
                reply += f"Found available courts at {h_name} on {date}\n"
                for court in available_courts:
                    data = court.get_attribute('value').split(';')
                    reply += f"Available Court: {data[0]} @ {data[3]} - {data[4]}\n"
            reply += "\n"
        if reply.strip() == "":
            bot.send_message(message.chat.id, f"{h_name} has no available courts.")
        else:
            bot.send_message(message.chat.id, reply)
bot.polling()
