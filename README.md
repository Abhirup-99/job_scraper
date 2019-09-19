# Job Scraper
A console program to scrape job opportunities from company job boards. Works for both full-time and internships!

## Installation
Install Selenium: `pip install selenium`

Install BeautifulSoup: `pip install beautifulsoup4`

## Usage
`$ python3 job_scraper.py`

Requires the following files in the same directory:
* `already_seen_links.txt`
* `blacklisted_keywords.txt`
* `blacklisted_locations.txt`
* `blacklisted_position_titles.txt`
* `greenhouse_companies.json`
* `lever_companies.json`
* `required_keywords.txt`
* `selenium_companies.json`
* `whitelisted_locations.txt`
* `workday_companies.json`

and outputs a file: `scraped_positions.csv`

## File Structure
* `already_seen_links.txt`
   * List of URLs for job positions already viewed
* `blacklisted_keywords.txt`
   * List of keywords that you don't want to appear in a job position title
   * Filtering detects the keywords even if they're not full words
   * **Example**: If `blacklisted_keywords` contains `intern`, it will remove positions titled `Software Development Intern` and `International Project Development`
* `blacklisted_locations.txt`
   * List of locations that you don't want to appear in a job position location
   * Filtering only looks for exact matches
   * **Example**: If `blacklisted_locations` contains `Las Vegas`, it will remove a position whose location is `Las Vegas` but _not_ `Las Vegas, NV, USA`
* `blacklisted_position_titles.txt`
   * List of phrases that you don't want to appear in a job position title
   * Filtering only detects the position title if it is at the beginning of a given job position title
   * **Example**: If `blacklisted_position_titles` contains `VP`, it will remove positions titled `VP of Operations` but _not_ `Operational VP`
* `chromedriver`
   * Used by Selenium to open Chrome window to load each website
* `greenhouse_companies.json`
* `job_scraper.py`
   * Contains all functions that scrapes websites and then filter the scraped positions
* `lever_companies.json`
   * JSON structure for companies using Lever job boards (e.g. `https://jobs.lever.co/<company name>`)
   * Uses the following format:
      ```
      {
         "Company": <Company Name>,
         "Link": <Optional, End of Link if Differs From Company Name>
      }
      ```
   * **Example #1** (Company name matches link) Company Name = `Google`, Greenhouse Link = `https://boards.greenhouse.io/google`
     ```
     {
        "Company": "Google"
     }
     ```
   * **Example #2**: (Company name doesn't match link) Company Name = `Google`, Greenhouse Link = `https://boards.greenhouse.io/googlejobs`
     ```
     {
        "Company": "Google",
        "Link": "googlejobs"
     }
     ```
* `required_keywords.txt`
* `selenium_companies.json`
* `whitelisted_locations.txt`
* `workday_companies.json`

## Current Issues
- [ ] Scraping Apple jobs board won't work in headless mode (using Selenium)
