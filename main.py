'''
Created on Feb 15, 2022

@author: Jeff
'''
import sys
from scraper import Scraper
import datetime
import os
from os.path import exists

if __name__ == '__main__':
    configFilePath = os.getcwd() + '\config.csv'

    weatherHistoryFileDataPath = "C:/"
    weatherFileDataPath = "C:/"
    url = "ny/buffalo/KBUF/date/"
    
    if exists(configFilePath):
        with open(configFilePath,'r') as configFile:
            contents = configFile.read()
            data = contents.split(',')
            weatherFileDataPath = data[0]
            weatherHistoryFileDataPath = data[1]
            url = data[2]
    
    scrape = Scraper()
    now = datetime.datetime.now()
    endDate = datetime.date(now.year, now.month, now.day)
    prettyEndDate = endDate.strftime('%Y-%m-%d')
    
    altStartDate = datetime.date(2020, 8, 1)
    
    # Get start date from file
    if exists(weatherHistoryFileDataPath):
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
        
        lastDate = datetime.date(int(pastYear), int(pastMonth), int(pastDay))
        startDate = lastDate + datetime.timedelta(days=1)
    else:
        startDate = altStartDate
    
    scrapeLog = 'Scraping from: ' + str(startDate) + ' to: ' + prettyEndDate
    print(scrapeLog)
    
    scrape.scrape(startDate, endDate, weatherFileDataPath, url)
    sys.exit()