from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from getpass import getpass
import pandas as pd

# Get credentials from user
username_input = input('Enter your LinkedIn username: ')
password_input = getpass('Enter your LinkedIn password (input will be hidden): ')
company_links_file = input('Enter the name of the file with the company links (make sure it is on the same directory as the script): ')
output_file = input('Enter the name of the output file name: ')
company_links = []

# Open the file with the company links
with open(company_links_file, 'r') as f:
  company_links = f.read().splitlines()

# Create an empty list to store the scraped data
companies_data = []

# Login to LinkedIn
def linkedin_login():
  # Create a new instance of the Chrome driver
  driver = webdriver.Chrome()

  # Go to the LinkedIn login page
  driver.get('https://www.linkedin.com/login')

  # Find the username & password elements & fill them with the login credentials
  username = driver.find_element(By.ID, 'username')
  username.send_keys(username_input) 
  password = driver.find_element(By.ID, 'password')
  password.send_keys(password_input)

  # Find & click the login button
  login_button = driver.find_element(By.CLASS_NAME, 'btn__primary--large')
  login_button.click()

  return driver

# Selenium function to scrape LinkedIn
def linkedin_scrape(company_links):

  driver = linkedin_login()

  # Wait for the page to load
  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'share-box-feed-entry__avatar')))

  print('Scraping started!')

  # Loop through the company links
  for link in company_links:
    # Go to company about
    driver.get(link + '/about/')

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'text-heading-xlarge')))

    # Get the page source
    html = driver.page_source

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    # Find company name
    company_name = soup.find(
      'h1',
      {'class': 'org-top-card-summary__title'}
    ).find('span',{'dir': 'ltr'}).text.strip()

    # Find company description
    company_description = soup.find('p', {'class': 'break-words white-space-pre-wrap t-black--light text-body-medium'}).text.strip()

    # Find company details
    company_details = soup.find('dl', {'class': 'overflow-hidden'})

    for detail in company_details.find_all('dt'):
      if detail.text.strip() == 'Website':
        company_website = detail.find_next_sibling('dd').find('a').get('href').strip()
      elif detail.text.strip() == 'Industry':
        company_industry = detail.find_next_sibling('dd').text.strip()
      elif detail.text.strip() == 'Company size':
        company_size = detail.find_next_sibling('dd').text.strip()

        # format company size
        company_size = company_size.replace('employees', '').strip()


    # Push the data into the list
    companies_data.append({
      'company_name': company_name,
      'company_description': company_description,
      'company_website': company_website,
      'company_industry': company_industry,
      'company_size': company_size
    })

  print('Scraping finished!')

  # Close the browser
  driver.quit()
  


# Run the function for company
linkedin_scrape(company_links)

print('Creating CSV file...')

# Create a Pandas DataFrame from the dictionary
company_df = pd.DataFrame(companies_data)

# Save the DataFrame as a CSV file
company_df.to_csv(output_file, index=False ,encoding='utf-8')

print('CSV file created!')

