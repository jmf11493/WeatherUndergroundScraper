'''
Created on Feb 15, 2022

@author: Jeff
'''

import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class Scraper(object):
    '''
    classdocs
    '''
    # TODO use actual date class that will account for leap year
    days   = [31, 28, 31, 30, 30, 31, 31, 31, 30, 31, 30, 31]
    url = "https://www.wunderground.com/history/daily/us/"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    weatherFileDataPath = ""
    
    weatherHistory = 'Weather_History.txt'
    weatherSunData = 'Weather_Sun_Data.txt'
    weatherObservations = 'Weather_Observations.txt'

    def __init__(self):
        '''
        Constructor
        '''
    def scrape(self, startYear, startMonth, startDay, endYear, endMonth, endDay, weatherFileDataPath, url):
        allDone = False
        self.weatherFileDataPath = weatherFileDataPath
        self.url = self.url + url
        # TODO don't hard code the end year
        for year in range(startYear, 2023):
            for month in range(startMonth, 13):
                for day in range(startDay, self.days[month-1]+1):
                    date = str(year) + '-' + str(month) + '-' + str(day)
                    print(date)
                    tempUrl = self.url + date
                    hasException = False
                    exceptionMessage = ''
                    sleepCount = 1
                    retryCount = 10
                    retry = 1
                    while retry < retryCount:
                        try:
                            data_arr = self.getPageData(tempUrl, sleepCount)
                            historyData = self.getHistoryData(data_arr, date)
                            sunData = self.getSunData(data_arr, date)
                            observationData = self.getObservationData(data_arr, date, retry)
                            hasException = False
                            break
                        except Exception as err:
                            # implement retry
                            hasException = True
                            exceptionMessage = str(err)
                            print('Error with date: ' + date + ' error: ' + exceptionMessage)
                            print('Retry Attempt: ' + str(retry))
                            sleepCount += 1
                            retry += 1
                            
                    if not hasException:
                        self.appendToFile(self.weatherFileDataPath + self.weatherHistory, historyData)
                        self.appendToFile(self.weatherFileDataPath + self.weatherSunData, sunData)
                        self.appendToFile(self.weatherFileDataPath + self.weatherObservations, observationData)
                    else:
                        print('Error with date: ' + date + ' writing to log')
                        self.appendToFile(self.weatherFileDataPath + 'log.txt', date + ' Error: ' + exceptionMessage + '\n')
                    if year == endYear and month == endMonth and day == endDay:
                        print('All Done')
                        allDone = True
                        break
                    if day == self.days[month-1]:
                        startDay = 0
                    startDay+=1
                if allDone:
                    break
                if startMonth == 12:
                    startMonth = 0
                startMonth+=1
            if allDone:
                break
        self.driver.close()

    def getPageData(self, tempUrl, sleepCount):
        self.driver.get(tempUrl)
        time.sleep(sleepCount)
        html = self.driver.page_source
         
        soup = BeautifulSoup(html, "html.parser")
        # sometimes the data is an empty span which messes up the indexes
        # this corrects for that
        for span in soup.find_all('span'):
            if span.get_text() == '':
                span.string = '-'
        results = soup.find_all('table')
        text = ''
        for result in results:
            text = text + result.get_text("|")
        remove_unicode = text.encode("ascii", "ignore").decode()
        cleaned_string = remove_unicode.replace("Polygon", "")
        cleaned_string = cleaned_string.replace("||", " ")
        data_arr = (cleaned_string.split("|"))
        
        return data_arr
    
    def appendToFile(self, fileName, information):
        file = open(fileName, "a")
        file.write(information)
        file.close()
    
    def getHistoryData(self, data_arr, date):
        tempHighAvgRecord = [date, 'temperature_high', data_arr[4], data_arr[5], data_arr[6]]
        tempLowAvgRecord = [date, 'temperature_low', data_arr[8], data_arr[9], data_arr[10]]
        tempAvgAvgRecord = [date, 'temperature_avg', data_arr[12], data_arr[13], data_arr[14]]
        precipAvgRecord = [date, 'precipitation', data_arr[19], data_arr[20], data_arr[21]]
#         dewpointTempAvgRecord = [date, 'dew_point', data_arr[26], data_arr[27], data_arr[28]]
        dewpointTempHighAvgRecord = [date, 'dew_point_high', data_arr[30], data_arr[31], data_arr[32]]
        dewpointTempLowAvgRecord = [date, 'dew_point_low', data_arr[34], data_arr[35], data_arr[36]]
        dewpointTempAvgAvgRecord = [date, 'dew_point_avg', data_arr[38], data_arr[39], data_arr[40]]
        windAvgRecord = [date, 'wind', data_arr[45], data_arr[46], data_arr[47]]
        visibilityAvgRecord = [date, 'visibility', data_arr[49], data_arr[50], data_arr[51]]
         
        threeColumns = [
            tempHighAvgRecord, 
            tempLowAvgRecord, 
            tempAvgAvgRecord,
            precipAvgRecord,
#             dewpointTempAvgRecord,
            dewpointTempHighAvgRecord,
            dewpointTempLowAvgRecord,
            dewpointTempAvgAvgRecord,
            windAvgRecord,
            visibilityAvgRecord
        ]
         
        historyTable = ''
        historyTableToFile = ''
        for row in threeColumns:
            historyTable += '\t'.join(row) + '\n'
            historyTableToFile += ','.join(row) + '\n'
        print(historyTable)
        
        return historyTableToFile
    
    def getSunData(self, data_arr, date):
        dayLength = data_arr[63]
        sunrise = data_arr[64]
        sunset = data_arr[65]
         
        print('Day Length: ' + dayLength)
        print('Sunrise: ' + sunrise)
        print('Sunset: ' + sunset)
        sunData = ','.join([date, dayLength, sunrise, sunset]) + '\n'
        
        return sunData
    
    def getObservationData(self, data_arr, date, retry):
        i = 0
        #sometimes this can be off by 2
        startIndex = 87 
        if data_arr[startIndex].strip() == 'F':
            if retry < 10:
                raise Exception('Offset is messed up refresh page')
            print('offset changed to 85')
            startIndex = 85
        table = ''
        tableToFile = ''
        # sometimes there are more than 24 entries as they report multiple times per hour
        # TODO need to account for this, see dates 2022-4-12 - 2022-4-17
        while i < 24:
            if startIndex > len(data_arr)-1:
                break
            timeOfDay     = data_arr[startIndex]
            temp          = data_arr[startIndex+1]
            dew           = data_arr[startIndex+3]
            humidity      = data_arr[startIndex+5]
            wind          = data_arr[startIndex+7]
            windSpeed     = data_arr[startIndex+8]
            windGust      = data_arr[startIndex+10]
            pressure      = data_arr[startIndex+12]
            precipitation = data_arr[startIndex+14]
            condition     = data_arr[startIndex+16]
            startIndex+=17
            row = [date, timeOfDay, temp, dew, humidity, wind, windSpeed, windGust, pressure, precipitation, condition]
            table+= '\t'.join(row) + '\n'
            tableToFile += ','.join(row) + '\n'
            i+=1
        print(table)
        
        return tableToFile
# indexes 4,5,6 actual high temperature, historic avg, record
# indexes 8,9,10 actual low temp, historic avg, record
# indexes 12, 13, 14 day average temp actual, historic avg, record
# indexes 19, 20, 21, precipitation (inches) actual, historic avg, record
# indexes 26, 27, 28 dew point F actual, historic avg, record
# indexes 30, 31, 32 dew point high, historic avg, record
# indexes 34, 35, 36 dew point low, historic avg, record
# indexes 38, 39, 40 dew point avg, historic avg, record
# indexes 45, 46, 47 wind MPH actual, historic avg, record
# indexes 49, 50, 51 visibility actual, historic avg, record
# indexes 63 day length
# indexes 64 sun rise
# indexes 65 sun set



# indexes 87 12:00 AM
# indexes 88 temperature
# indexes 90 dew point
# indexes 92 humidity
# indexes 94 wind (string)
# indexes 95 wind speed (mph)
# indexes 97 wind gust (mph)
# indexes 99 pressure (in)
# indexes 101 precipitation
# indexes 103 condition
# indexes 104 time (+17)
# repeat (24 rows)    