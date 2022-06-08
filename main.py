'''
Created on Feb 15, 2022

@author: Jeff
'''
import sys
from scraper import Scraper
import datetime
import os
if __name__ == '__main__':
    config_file_path = os.getcwd() + '\config.csv'

    weatherHistoryFileDataPath = ""
    weatherFileDataPath = ""
    url = ""
    with open(config_file_path,'r') as config_file:
        contents = config_file.read()
        data = contents.split(',')
        weatherFileDataPath = data[0]
        weatherHistoryFileDataPath = data[1]
        url = data[2]
    scrape = Scraper()
    now = datetime.datetime.now()
    year = int(now.year)
    month = int(now.month)
    # always get the previous day
    day = int(now.day - 1)
    
    file = open(weatherHistoryFileDataPath, "r")
    lastLine = file.readlines()[-1]
    file.close()
    pastYear = None
    pastMonth = None
    pastDay = None
    pastDate = None
    if lastLine:
        pastDate = lastLine.split(',')[0]
        pastDateSplit = pastDate.split('-')
        pastYear = int(pastDateSplit[0])
        pastMonth = int(pastDateSplit[1])
        pastDay = int(pastDateSplit[2])
    today = '-'.join([str(year),str(month),str(day)])
    scrapeLog = 'Scraping from: ' + str(pastDate) + ' to: ' + today
    print(scrapeLog)
    
    scrape.scrape(pastYear, pastMonth, pastDay, year, month, day, weatherFileDataPath, url)
    sys.exit()