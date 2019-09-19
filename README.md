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
   * **Example**: If `blacklisted_keywords` contains `intern`, it will remove positions titled `Software Development Intern` _and_ `International Project Development`
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
   * JSON structure for companies using Greenhouse job boards (e.g. `https://boards.greenhouse.io/<company name>`)
   * Uses the following format:
      ```
      {
         "Company": <Company Name>,
         "Link": <Optional, End of Link if Differs From Company Name>
      }
      ```
   * **Example #1**: Company name matches link
       * Company Name = `Google`, Greenhouse Link = `https://boards.greenhouse.io/google`
         ```
         {
            "Company": "Google"
         }
         ```
   * **Example #2**: Company name doesn't match link
       * Company Name = `Google`, Greenhouse Link = `https://boards.greenhouse.io/googlejobs`
         ```
         {
            "Company": "Google",
            "Link": "googlejobs"
         }
         ```
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
   * **Example #1**: Company name matches link
       * Company Name = `Google`, Greenhouse Link = `https://jobs.lever.co/google`
         ```
         {
            "Company": "Google"
         }
         ```
   * **Example #2**: Company name doesn't match link
       * Company Name = `Google`, Greenhouse Link = `https://jobs.lever.co/googlejobs`
         ```
         {
            "Company": "Google",
            "Link": "googlejobs"
         }
         ```
* `required_keywords.txt`
    * List of keywords where at least 1 must appear in each job position title
    * Filtering detects the keywords even if they're not full words
    * This overrides the `blacklisted_keywords` list (in other words, if a position title contains keywords from both `required_keywords` and `blacklisted_keywords`, it will not remove that position title
        * However, if a position title is in `required_keywords` and `blacklisted_position_titles`, it will be removed
    * **Example**: If `required_keywords` contains `intern`, it will only keep position titles such as `Software Development Intern` _and_ `International Project Development`
* `selenium_companies.json`
    * Formatted in the following way:
      ```
      {
          "Company Name": <Company Name>
          "Company Website": <Full URL>
          "Job Item": <CSS selector of HTML element that defines a job>,
          "Job Item Title": <CSS selector of HTML element for the job's title within Job Item>,
          "Job Item Link": <(optional, can be ignored if Job Item element contains the URL href) CSS selector of HTML element for the job's link within Job Item>,
          "Job Item Location": <CSS selector of HTML element for the job's location within Job Item>,
          "Prereq Clicks": <(optional) XPath selector of HTML element that needs to be clicked in order for job board to display>
      }
      ```
    * **Example**:
        * This is a snippet of the HTML for a given job board:
          ```
          ...
          <div id="job-board-body">
            <div class="job-position">
              <span class="job-title">This is the job's position title</span>
              <a class="job-link" href="https://bierman.io">This is a link for more info about the job</a>
              <span class="job-location">This is the job's location</span>
            </div>
            <div class="job-position"> ... </div>
            <div class="job-position"> ... </div>
            <div class="job-position"> ... </div>
            <div class="job-position"> ... </div>
          </div>
          ...
          ```
        * Job Item = `#job-board-body > .job-position`
        * Job Item Title = `span.job-title`
        * Job Item Link = `a.job-link`
        * Job Item Location = `span.job-location`
* `whitelisted_locations.txt`
    * List of accepted locations
    * Filtering only looks for exact matches
   * **Example**: If `whitelisted_locations` contains `Las Vegas`, it will keep a position whose location is `Las Vegas` but _not_ `Las Vegas, NV, USA`
* `workday_companies.json`
    * Formatted in the following way:
      ```
      {
          "Company": <Company Name>
          "Link": <Full URL>
      }
      ```

## Current Issues
- [ ] Scraping Apple jobs board won't work in headless mode (using Selenium)
- [ ] Allow more than one prerequisite click for Selenium job scraping
