from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
import smtplib
from email.mime.base import MIMEBase
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# Initialize the WebDriver for Chrome browser
driver = webdriver.Chrome()

url = "https://www.ca.kayak.com/?ispredir=true"

driver.get(url)
sleep(5)


def load_more():
    '''
    Function to get more results by clicking the "load more" button on the website.
    Waits for a random interval between 25-35 seconds to simulate human interaction
    '''
    try:
        more_results = '//a[@class = "ULvh-button show-more-button"]'
        driver.find_element("xpath",(more_results)).click()
        print('sleeping...')
        sleep(randint(25,35))
    except:
        pass

def start_kayak(city_from, city_to, date_start, date_end):
    '''
    Function to construct the desired url based on user input with flexible dates.
    Also initiates the scraping process.
    '''
    kayak = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')
    driver.get(kayak)
    sleep(randint(8,10))

    try:
        pop_up = '//div[@class = "bBPb-close"]'
        driver.find_element("xpath",(pop_up)).click()   # Closes the "get prices alert" pop-up at the bottom right of the screen
    except Exception as e:
        pass
    sleep(randint(40,50))
    print("Loading...")

    print('Starting first page scrape.....')
    df_flights_best = page_scrape()
    df_flights_best['sort'] = 'best'
    sleep(randint(40,50))
    
    
    elements_path = '//*[contains(@id,"FlexMatrixCell")]'
    matrix = driver.find_elements("xpath",(elements_path))      # Getting the prices from the FlexMatrix
    matrix_prices = [price.text.replace('$','').replace(',', '').strip() for price in matrix if price.text != '']
    matrix_prices = list(map(int,matrix_prices))    # Converting prices to int and storing in list
    matrix_min = min(matrix_prices)                 # Calculate the cheapest price
    matrix_avg = round(sum(matrix_prices)/len(matrix_prices), 2)    # Calculate the average price

    print('Loading cheapest prices...')
    cheap_prices = '//*[@id="listWrapper"]/div/div[2]/div[1]'
    driver.find_element("xpath",(cheap_prices)).click()
    sleep(randint(40,50))
    print("Loading...")

    print("Starting second page scrape...")
    df_flights_cheap = page_scrape()    
    df_flights_cheap['sort'] = 'cheap'
    sleep(randint(40,50))

    print('Loading shortest duration...')
    shortest_duration = '//*[@id="listWrapper"]/div/div[2]/div[3]'
    driver.find_element("xpath",(shortest_duration)).click()
    sleep(randint(40,50))
    print("Loading...")

    print("Starting third page scrape...")
    df_flights_duration = page_scrape()
    df_flights_duration['sort'] = 'fast'
    sleep(randint(40,50))
    # Directory path
    directory = 'search_backups'

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Concat the dataframes and save to directory
    frames = [df_flights_cheap,df_flights_best,df_flights_duration]
    final_df = pd.concat(frames)
    file_name = '{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y%m%d-%H%M"),city_from,city_to,date_start,date_end)
    directory = 'search_backups'
    file_path = os.path.join(directory, file_name)
    os.makedirs(directory, exist_ok=True)
    final_df.to_excel(file_path, index=False)
    print('Saved the dataframe')

    # Check whether the file is there
    if os.path.exists(file_path):
        print(f"File saved successfully!")
    else:
        print(f"Failed to save file at: {file_path}")
        raise FileNotFoundError(f"No such file or directory!")
    
    username = "INSERT YOUR GMAIL ADDRESS HERE"
    password = "INSERT YOUR APP PASSWORD"

    try:
        # Set up the SMTP server connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username,password)     # Log in to the SMTP server
        
        # Create a MIMEMultipart message object
        message = MIMEMultipart()
        message['From'] = 'YOUR GMAIL ADDRESS'
        message['To'] = 'RECEIVER EMAIL ADDRESS'
        message['Subject'] = 'Flight Scraper'

        # Create the email message with the flight details
        body = f'Flight From: {city_from} Destination: {city_to}\nCheapest Flight: ${matrix_min}\nAverage Price: ${matrix_avg}\nExcel spreadsheet with prices attached below'
        message.attach(MIMEText(body, 'plain'))

        # Attach the xcel sheet with flight details to the email message
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}',
                )
                message.attach(part)
        except Exception as e:
            print(f"Failed to read and attach file: {file_path}")
            print(f"Error: {e}")
            raise
        
        server.sendmail('yoonki313@gmail.com','jessicathomas79336@gmail.com',message.as_string())
        print("Email successfully sent!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
    # Close the SMTP server connection
        server.quit()


def page_scrape():
    '''
    Function to perform scraping of the website and extract the flight details.
    Returns the dataframe containing flight data.
    '''
    xp_sections = '//div[@class="xdW8"]'
    sections = driver.find_elements("xpath",(xp_sections))
    sections_list = [value.text for value in sections]
    section_out_list = sections_list[::2]
    section_in_list = sections_list[1::2]

    if section_out_list == []:
        raise SystemExit
    
    # Get the flight duration and section names for outbound and inbound flights
    out_duration = []
    out_section_names = []
    for n in section_out_list:
        out_section_names.append(''.join(n.split()[2:5]))
        out_duration.append(''.join(n.split()[0:2]))

    in_duration = []
    in_section_names = []
    for n in section_in_list:
        in_section_names.append(''.join(n.split()[2:5]))
        in_duration.append(''.join(n.split()[0:2]))
    
    # Get the flight dates
    xp_dates = '//div[@class="c9L-i"]'
    dates = driver.find_elements("xpath",(xp_dates))
    dates_list = [value.text for value in dates]
    out_date_list = dates_list[::2]
    in_date_list = dates_list[1::2]

    out_day = [value.split()[0] for value in out_date_list]
    out_weekday = [value.split()[1] for value in out_date_list]
    in_day = [value.split()[0] for value in in_date_list]
    in_weekday = [value.split()[1] for value in in_date_list]

    # Get the prices
    xp_prices = '//div[@class="f8F1-price-text"]'
    prices = driver.find_elements("xpath",xp_prices)
    prices_list = [price.text.replace('$','').replace(',', '').strip() for price in prices if price.text != '']
    prices_list = list(map(int, prices_list))
    
    # Get the number of layovers 
    xp_stops = '//div[@class="JWEO"]/div[1]'
    stops = driver.find_elements("xpath", xp_stops)
    stops_list = [stop.text[0].replace("n","0") for stop in stops]
    out_stop_list = stops_list[::2]
    in_stop_list = stops_list[1::2]

    # Get the layover cities
    xp_stops_cities = '//div[@class="JWEO"]/div[2]'
    stops_cities = driver.find_elements("xpath",(xp_stops_cities))
    stops_cities_list = [stop.text for stop in stops_cities]
    out_stop_name_list = stops_cities_list[::2]
    in_stop_name_list = stops_cities_list[1::2]

    # Get the flight hours and airlines names 
    xp_schedule = '//div[@class="VY2U"]'
    schedules = driver.find_elements("xpath",(xp_schedule))
    hours_list=[]
    carrier_list=[]
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0])
        carrier_list.append(schedule.text.split('\n')[1])

    out_hours = hours_list[::2]
    in_hours = hours_list[1::2]
    out_carrier = carrier_list[::2]
    in_carrier = carrier_list[1::2]


    # Create the dataframe with the flight data
    cols = (['Departure Day', 'Departure Time', 'Price', 'Departure Weekday', 'Departure Airline', 'Departure Cities', 'Depature Duration', 'Departure Stops', 'Departure Stop Cities',
            'Return Day', 'Return Time', 'Return Weekday', 'Return Airline', 'Return Cities', 'Return Duration', 'Return Stops', 'Return Stop Cities'])
    
    flights_df = pd.DataFrame({'Departure Day' : out_day, 'Departure Weekday' : out_weekday, 'Departure Time' : out_hours, 'Departure Airline' : out_carrier, 'Departure Cities' : out_section_names, 'Depature Duration' : out_duration, 'Departure Stops' : out_stop_list, 'Departure Stop Cities' : out_stop_name_list,
            'Return Day' : in_day, 'Return Weekday' : in_weekday, 'Return Time' : in_hours, 'Return Airline' : in_carrier, 'Return Cities' : in_section_names, 'Return Duration' : in_duration, 'Return Stops' : in_stop_list, 'Return Stop Cities' : in_stop_name_list, 'Price' : prices_list}) [cols]
    
    flights_df['timestamp'] = strftime("%Y%m%d-%H%M")
    return flights_df

# Get user input for flight details
city_from = input("From city? ")
city_to = input("To city? ")
date_start = input("Departure date (YYYY-MM-DD)? ")
date_end = input("Return date (YYYY-MM-DD)? ")
'''
Example:
From city? YYC
To city? NYC
Departure date (YYYY-MM-DD)? 2024-09-25
Return date (YYYY-MM-DD)? 2024-10-01
'''

# Iterate to get flight details 5 times every 3 hours 
for n in range(0,5):
    start_kayak(city_from,city_to,date_start,date_end)
    print('Iteration {} was complete at {}'.format(n, strftime("%Y%m%d-%H%M")))
    # Wait 3 hours for next iteration
    sleep(60*60*3)
    print('Sleep finished.....')

driver.quit() 