# FlightScraper
Web scraping tool that extracts flight information from [Kayak.com](https://www.ca.kayak.com/). It takes user inputted departure city, destination city, departure date, and return date. Using the information given, it then performs a few iterations to collect flight data at intervals, saving the details in an excel file, and emails the collected data.

## Features
* Uses Selenium WebDriver to interact with the Kayak website.
* Scrapes flight information including departure and return times, airlines, durations, and prices.
* Supports flexible dates for flight searches.
* Iterates the scraping process at specified intervals to capture updated flight data.
* Exports the scraped data into a pandas DataFrame for further analysis or storage.
* Sends an email with the flight information attached as an excel file after each iteration.
* Stores the scraped data files in a directory.

## How to run
* Clone the repository. Ensure the required Python packages are installed.
* Open main.py and add your Gmail address and the receiver's email address in the respective sections.
* Finally, run the script.
* Provide the required inputs when prompted.
  
  Example:
  
  ![](https://github.com/jessicathomas13/FlightScraper/blob/main/imgs/terminal.jpg)

* The program will run for 5 iterations, scraping flight data every 3 hours and printing the status of each iteration. After each iteration, the scraped flight information will be emailed as an attachment and stored in the search_backups directory.
