# ActiveSG Scraper

This repo is for educational purposes only and not meant to be used as a tool to execute bookings.

### Prerequisites
- In order to run, you will need to have chromedriver installed and added to PATH.
- You will need to have an activesg account
- You will need to create a telegram bot
- Create `.env` and follow the structure as in `.env-sample`

### Installing dependencies
```
pip install -r requirements.txt
```

### Running script
```
python activesgscraper.py
```

### Available Telgram Bot commands
- `/halls`: Retrieves all available sports halls
- `/getslots <SPORTS_HALL_ID>`: Returns a list of available slots for booking for the specified `SPORTS_HALL_ID`
  - eg. `/getslots 296`: Gets available slots for the next 5 days for Clementi Sports Hall


Notes:
The script now only retrieves slots for Badminton Courts.