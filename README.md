# Job Scraper
A script to scrape job opportunities from company job boards. Works for both full-time and internships!

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

**Note**: There may be a console output that includes a list of locations, those are new locations that were found in scraped job positions that aren't in the `blacklisted_locations` and `whitelisted_locations`. Those job positions containing those new locations will still be in the output CSV file, but they'll need to be added to the blacklist/whitelist before running the script again.

### Recommended Usage Steps
1. Leave the following files as is `already_seen_links.txt`, `blacklisted_locations.txt`, `whitelisted_locations.txt` (it's set to locations that are non-remote and inside the US)
2. Leave all `.json` files as is
3. Add to `blacklisted_keywords.txt` and `blacklisted_position_titles.txt` with keywords and position titles that you don't want to appear in the filtered job positions
4. (Optional, not suggested for full-time) Add to `required_keywords.txt` with keywords that must be in each filtered job position title
5. Run `job_scraper.py`
6. If `Add each location to the whitelist or blacklist:` appears in the console, add each location to `blacklisted_locations.txt` or `whitelisted_locations.txt`
7. Open `scraped_positions.csv`, add each URL to `already_seen_links.txt` so they don't appear again when you run `job_scraper.py` again
8. It's recommended to run the script around once per week

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
- [ ] Expand this script to accommodate for more than just engineering/CS-related positions

## Company List
Company Name | Scraping Method | Status
--- | --- | ---
Apple | Selenium (custom) | Complete (doesn't work in headless mode)
Adobe | Workday | Complete
Affinity | Lever | Complete
Airbnb | Selenium | Complete
Asana | Greenhouse | Complete
Bolt | Lever | Complete
Coda | Selenium (custom) | Complete
Compass | Selenium | Complete
DoorDash | Selenium | Complete
Electronic Arts | Selenium (custom) | Complete
Envoy | Greenhouse | Complete
Epic Games | Workday | Complete
Even | Lever | Complete
Figma | Lever | Complete
GitHub | Greenhouse | Complete
Grammarly | Selenium | Complete
Hinge | Selenium | Complete
Honey | Selenium | Complete
Houzz | Lever | Complete
Hulu | Selenium (custom) | Complete
Instacart | Greenhouse | Complete
Intercom | Greenhouse | Complete
Invision | Greenhouse | Complete
Lattice | Lever | Complete
Lemonade | Selenium | Complete
LinkedIn | Selenium (custom) | Complete
Lyft | Selenium | Complete
MailChimp | Greenhouse | Complete
Mapbox | Selenium | Complete
Mixmax | Selenium | Broken (as of 9/19)
NerdWallet | Selenium | Complete
Nextdoor | Greenhouse | Complete
Niantic | Greenhouse | Complete
Oscar Health | Selenium | Complete
Opendoor | Lever | Complete
OpenTable | Greenhouse | Complete
Palantir | Lever | Complete
Plaid | Lever | Complete
Postmates | Greenhouse | Complete
Robinhood | Selenium | Complete
Rockstar Games | Selenium (custom) | Complete
SeatGeek | Greenhouse | Complete
Shopify | Selenium | Complete
Sketch | Selenium | Complete
Slack | Selenium | Complete
Snap | Workday | Complete
Sonder | Greenhouse | Complete
Splash | Greenhouse | Complete
Spotify | Selenium (custom) | Complete
Spoke | Lever | Complete
Square | Selenium | Broken (as of 9/19)
Stripe | Selenium | Complete
Textio | Lever | Complete
Tinder | Selenium | Complete
Thumbtack | Greenhouse | Complete
Topfunnel | Selenium | Complete
Ubisoft | Selenium (custom) | Complete
Udacity | Greenhouse | Complete
Udemy | Lever | Complete
Valve | Selenium | Complete
Vimeo | Greenhouse | Complete
VSCO | Selenium | Complete
Wealthfront | Lever | Complete
X | Selenium | Complete
Zendesk | Selenium (custom) | Complete
Zenimax | Selenium | Complete
Zillow Group | Workday | Complete
Zocdoc | Selenium | Complete
Zynga | Selenium | Complete
