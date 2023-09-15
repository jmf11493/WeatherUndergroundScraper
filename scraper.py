'''
Created on Feb 15, 2022

@author: Jeff
'''

import time
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime


class Scraper:
    '''
    classdocs
    '''
    url = "https://www.wunderground.com/history/daily/us/"
    driver = webdriver.Chrome()

    weatherFileDataPath = ""
    
    weatherHistory = 'Weather_History.txt'
    weatherSunData = 'Weather_Sun_Data.txt'
    weatherObservations = 'Weather_Observations.txt'
    
    def scrape(self, start_date, end_date, weather_file_data_path, url):
        self.weatherFileDataPath = weather_file_data_path
        self.url = self.url + url
        
        while start_date != end_date:
            year = start_date.year
            month = start_date.month
            day = start_date.day
            date = str(year) + '-' + str(month) + '-' + str(day)
            print(date)
            
            temp_url = self.url + date
            has_exception = False
            exception_message = ''
            sleep_count = 1
            retry_count = 10
            retry = 1
            
            while retry < retry_count:
                try:
                    print('attempting to get data')
                    data_arr = self.getPageData(temp_url, sleep_count)
                    print('get page data')
                    history_data = self.getHistoryData(data_arr, date)
                    print('get history data')
                    sun_data = self.getSunData(data_arr, date)
                    print('get sun data')
                    observation_data = self.getObservationData(data_arr, date, retry)
                    print('get observation data')
                    has_exception = False
                    break
                except Exception as err:
                    has_exception = True
                    exception_message = str(err)
                    print('Error with date: ' + date + ' error: ' + exception_message)
                    print('Retry Attempt: ' + str(retry))
                    sleep_count += 1
                    retry += 1
                    
            if not has_exception:
                print('append 1')
                self.appendToFile(self.weatherFileDataPath + self.weatherHistory, history_data)
                print('append 2')
                self.appendToFile(self.weatherFileDataPath + self.weatherSunData, sun_data)
                print('append 3')
                self.appendToFile(self.weatherFileDataPath + self.weatherObservations, observation_data)
            else:
                print('Error with date: ' + date + ' writing to log')
                self.appendToFile(self.weatherFileDataPath + 'log.txt', date + ' Error: ' + exception_message + '\n')
            
            start_date = start_date + datetime.timedelta(days=1)
        print('All Done')
        self.driver.quit()

    def getPageData(self, temp_url, sleep_count):
        print('get page data function')
        get_page = False
        while not get_page:
            try:
                self.driver.get(temp_url)
                get_page = True
            except Exception as e:
                print(e)
        time.sleep(sleep_count)
        print('get page source')
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
    
    def appendToFile(self, file_name, information):
        file = open(file_name, "a")
        file.write(information)
        file.close()
    
    def getHistoryData(self, data_arr, date):
        temp_high_avg_record = [date, 'temperature_high', data_arr[4], data_arr[5], data_arr[6]]
        temp_low_avg_record = [date, 'temperature_low', data_arr[8], data_arr[9], data_arr[10]]
        temp_avg_avg_record = [date, 'temperature_avg', data_arr[12], data_arr[13], data_arr[14]]
        precip_avg_record = [date, 'precipitation', data_arr[19], data_arr[20], data_arr[21]]
#         dewpointTempAvgRecord = [date, 'dew_point', data_arr[26], data_arr[27], data_arr[28]]
        dewpoint_temp_high_avg_record = [date, 'dew_point_high', data_arr[30], data_arr[31], data_arr[32]]
        dewpoint_temp_low_avg_record = [date, 'dew_point_low', data_arr[34], data_arr[35], data_arr[36]]
        dewpoint_temp_avg_avg_record = [date, 'dew_point_avg', data_arr[38], data_arr[39], data_arr[40]]
        wind_avg_record = [date, 'wind', data_arr[45], data_arr[46], data_arr[47]]
        visibility_avg_record = [date, 'visibility', data_arr[49], data_arr[50], data_arr[51]]
         
        three_columns = [
            temp_high_avg_record,
            temp_low_avg_record,
            temp_avg_avg_record,
            precip_avg_record,
#             dewpointTempAvgRecord,
            dewpoint_temp_high_avg_record,
            dewpoint_temp_low_avg_record,
            dewpoint_temp_avg_avg_record,
            wind_avg_record,
            visibility_avg_record
        ]
         
        history_table = ''
        history_table_to_file = ''
        for row in three_columns:
            history_table += '\t'.join(row) + '\n'
            history_table_to_file += ','.join(row) + '\n'
        print(history_table)
        
        return history_table_to_file
    
    def getSunData(self, data_arr, date):
        day_length = data_arr[63]
        sunrise = data_arr[64]
        sunset = data_arr[65]
         
        print('Day Length: ' + day_length)
        print('Sunrise: ' + sunrise)
        print('Sunset: ' + sunset)
        sun_data = ','.join([date, day_length, sunrise, sunset]) + '\n'
        
        return sun_data
    
    def getObservationData(self, data_arr, date, retry):
        i = 0
        # sometimes this can be off by 2
        start_index = 87
        if data_arr[start_index].strip() == 'F':
            if retry < 10:
                raise Exception('Offset is messed up refresh page')
            print('offset changed to 85')
            start_index = 85
        table = ''
        table_to_file = ''
        print(data_arr)
        while start_index < len(data_arr)-1:
            time_of_day = data_arr[start_index]
            temp = data_arr[start_index+1]
            dew = data_arr[start_index+3]
            humidity = data_arr[start_index+5]
            wind = data_arr[start_index+7]
            wind_speed = data_arr[start_index+8]
            wind_gust = data_arr[start_index+10]
            pressure = data_arr[start_index+12]
            precipitation = data_arr[start_index+14]
            condition = data_arr[start_index+16]
            start_index += 17
            row = [date, time_of_day, temp, dew, humidity, wind, wind_speed, wind_gust, pressure, precipitation, condition]
            table += '\t'.join(row) + '\n'
            table_to_file += ','.join(row) + '\n'
            i += 1
        print(table)
        
        return table_to_file
