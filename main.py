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