import csv, json, requests, string
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from urllib.request import Request, urlopen


# Scrapes all positions from each Greenhouse job board in input list
# Outputs each position with company name, position title, URL, and position location
def get_positions_on_greenhouse(job_boards):
    root_link = "https://boards.greenhouse.io/"
    all_positions = []

    for job_board in job_boards:
        print("\tScraping for " + job_board["Company"] + "...", end=" ", flush=True)

        page = requests.get(root_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(root_link + job_board["Link"])
        sections = BeautifulSoup(page.text, 'html.parser').find_all("section", {"class": "level-0"})

        if len(sections) == 0:
            print("ERROR:", job_board["Company"], "could not be scraped!")
        else:
            for section in sections:
                for position in section.find_all("div", {"class": "opening"}):
                    all_positions.append({
                        "Company": job_board["Company"],
                        "Title": position.find("a").getText().strip(),
                        "Link": ("" if position.find("a")['href'].startswith("https") else root_link[:-1]) + position.find("a")['href'],
                        "Location": position.find("span", {"class": "location"}).getText().strip()
                    })

            print("Done")

    return all_positions


# Scrapes all positions from each Lever job board in input list
# Outputs each position with company name, position title, URL, and position location
def get_positions_on_lever(job_boards):
    root_link = "https://jobs.lever.co/"
    all_positions = []

    for job_board in job_boards:
        print("\tScraping for " + job_board["Company"] + "...", end=" ", flush=True)

        page = requests.get(root_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(root_link + job_board["Link"])
        positions = BeautifulSoup(page.text, 'html.parser').find_all("div", {"class": "posting"})

        if len(positions) == 0:
            print("ERROR:", job_board["Company"], "could not be scraped!")
        else:
            for position in positions:
                if position.find("span", {"class": "sort-by-commitment"}):
                    all_positions.append({
                        "Company": job_board["Company"],
                        "Title": position.find("h5").getText() + " (" + position.find("span", {
                            "class": "sort-by-commitment"}).getText() + ")",
                        "Link": position.find("a", {"class": "posting-title"})['href'],
                        "Location": position.find("span", {"class": "sort-by-location"}).getText()
                    })
                else:
                    all_positions.append({
                        "Company": job_board["Company"],
                        "Title": position.find("h5").getText(),
                        "Link": position.find("a", {"class": "posting-title"})['href'],
                        "Location": position.find("span", {"class": "sort-by-location"}).getText()
                    })

            print("Done")

    return all_positions


# Helper function for get_positions_on_workday
# Finds the location of a desired key
def extract_key(elem, key):
    if isinstance(elem, dict):
        if key in elem:
            return elem[key]
        for k in elem:
            item = extract_key(elem[k], key)
            if item is not None:
                return item
    elif isinstance(elem, list):
        for k in elem:
            item = extract_key(k, key)
            if item is not None:
                return item
    return None


# Helper function for get_positions_on_workday
# Scrapes the JSON of a given URL
def get_request_to_dict(link, company_name):
    req = Request(link)
    req.add_header("Accept", "application/json,application/xml")

    try:
        raw_page = urlopen(req).read().decode()
        page_dict = json.loads(raw_page)
    except:
        print("ERROR:", company_name, "could not be scraped!")
        page_dict = {}

    return page_dict


# Scrapes all positions from each Workday job board in input list
# Outputs each position with company name, position title, URL, and position location
def get_positions_on_workday(job_boards):
    all_positions = []

    for job_board in job_boards:
        print("\tScraping for " + job_board["Company"] + "...", end=" ", flush=True)

        postings_page_dict = get_request_to_dict(job_board["Link"], job_board["Company"])
        if len(postings_page_dict) > 0:
            base_url = job_board["Link"][:job_board["Link"].index('.com') + 4]
            pagination_end_point = base_url
            for end_point in extract_key(postings_page_dict, 'endPoints'):
                if end_point['type'] == "Pagination":
                    pagination_end_point += end_point['uri'] + '/'
                    break

            while True:
                postings_list = extract_key(postings_page_dict, 'listItems')
                if postings_list is None:
                    break

                paginated_urls = []
                for position in postings_list:
                    paginated_urls.append({
                        "Company": job_board["Company"],
                        "Title": position["title"]["instances"][0]["text"],
                        "Link": base_url + position["title"]["commandLink"],
                        "Location": position["subtitles"][0]["instances"][0]["text"] if ", More..." not in position["subtitles"][0]["instances"][0]["text"] else position["subtitles"][0]["instances"][0]["text"][:position["subtitles"][0]["instances"][0]["text"].index(", More...")]
                    })

                all_positions += paginated_urls
                postings_page_dict = get_request_to_dict(pagination_end_point + str(len(all_positions)), job_board["Company"])

            print("Done")

    return all_positions


# Scrapes all positions from companies that use a custom job board
# Outputs each position with company name, position title, URL, and position location
def get_positions_using_selenium(job_boards):
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    for job_board in job_boards:
        print("\tScraping for " + job_board.get("Company Name") + "...", end=" ", flush=True)

        browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
        browser.get(job_board.get("Careers Website"))

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, job_board.get("Job Item"))))

            if job_board.get("Prereq Clicks") is not None:
                browser.find_element_by_xpath(job_board.get("Prereq Clicks")).click()

            for job in browser.find_elements_by_css_selector(job_board.get("Job Item")):
                all_positions.append({
                    "Company": job_board.get("Company Name"),
                    "Title": job.find_element_by_css_selector(job_board.get("Job Item Title")).text,
                    "Link": job.get_attribute("href") if job_board.get("Job Item Link") is None else job.find_element_by_css_selector(job_board.get("Job Item Link")).get_attribute("href"),
                    "Location": "" if job_board.get("Job Item Location") is None else ' '.join([location.text for location in job.find_elements_by_css_selector(job_board.get("Job Item Location"))])
                })

            print("Done")
        except:
            print("ERROR:", job_board.get("Company Name"), "could not be scraped!")

        browser.quit()

    return all_positions


# Scrapes all positions from Apple's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_apple_positions(link):
    print("\tScraping for Apple...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    while True:
        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#active-search-results")))

            for job in browser.find_elements_by_css_selector("table > tbody"):
                all_positions.append({
                    "Company": "Apple",
                    "Title": job.find_element_by_css_selector("tr > td.table-col-1 > a").text,
                    "Link": job.find_element_by_css_selector("tr > td.table-col-1 > a").get_attribute("href"),
                    "Location": job.find_element_by_css_selector("tr > td.table-col-2 > span").text
                })

            if "disabled" in browser.find_element_by_css_selector("nav.pagination > ul > li.pagination__next span.next").get_attribute("class"):
                break
            else:
                browser.find_element_by_css_selector("nav.pagination > ul > li.pagination__next").click()
        except:
            print("ERROR: Apple could not be scraped!")
            all_positions = []
            break

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from Coda's job postings on LinkedIn
# Outputs each position with company name, position title, URL, and position location
def scrape_coda_positions(link):
    print("\tScraping for Coda...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list")))

        for job in browser.find_elements_by_css_selector("ul.jobs-search__results-list > li.job-result-card"):
            all_positions.append({
                "Company": "Coda",
                "Title": job.find_element_by_css_selector("div.job-result-card__contents > h3.job-result-card__title").text,
                "Link": job.find_element_by_css_selector("a.result-card__full-card-link").get_attribute("href")[:job.find_element_by_css_selector("a.result-card__full-card-link").get_attribute("href").index("?")],
                "Location": job.find_element_by_css_selector("div.job-result-card__contents > div.job-result-card__meta > span.job-result-card__location").text
            })
    except:
        print("ERROR: Coda could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from EA's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_ea_positions(link):
    print("\tScraping for Electronic Arts...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    total_page_count = int(browser.find_element_by_css_selector("div.pagination > a:nth-child(3)").get_attribute("data-page"))

    for page in range(1, total_page_count + 1):
        # wait for results to load
        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".search-results-view.loading-context")))

            # scrape all positions from the current page
            for job in browser.find_elements_by_css_selector("div.search-results-view.loading-context tbody > tr"):
                all_positions.append({
                    "Company": "Electronic Arts",
                    "Title": job.find_element_by_css_selector("td:nth-child(2)").text,
                    "Link": job.find_element_by_css_selector("td:nth-child(1) > a").get_attribute("href"),
                    "Location": job.find_element_by_css_selector("td:nth-child(4)").text
                })

            # move to next page
            if page == 1:
                browser.find_element_by_css_selector("div.pagination > a:nth-child(4)").click()
            elif page < total_page_count:
                browser.find_element_by_css_selector("div.pagination > a:nth-child(5)").click()
            time.sleep(1)

        except:
            print("ERROR: Electronic Arts (page ", page, ") could not be scraped!", sep="")
            all_positions = []
            break

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from Hulu's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_hulu_positions(link):
    print("\tScraping for Hulu...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, "positions")))

        browser.find_element_by_css_selector("#category_filters > div:nth-child(16)").click()

        prev_height = 0
        new_height = int(browser.execute_script("return document.body.scrollHeight"))
        while prev_height < new_height:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            prev_height = new_height
            new_height = int(browser.execute_script("return document.body.scrollHeight"))

        for job in browser.find_elements_by_css_selector("#positions > .job-listing"):
            all_positions.append({
                "Company": "Hulu",
                "Title": job.find_element_by_css_selector(".job-info > h4 > a").text,
                "Link": job.find_element_by_css_selector(".job-info > h4 > a").get_attribute("href"),
                "Location": job.find_element_by_css_selector(".job-info > span:nth-child(6)").text
            })
    except:
        print("ERROR: Hulu could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from LinkedIn's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_linkedin_positions(link):
    print("\tScraping for LinkedIn...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list")))

        while True:
            try:
                browser.find_element_by_css_selector("button.see-more-jobs").click()
                time.sleep(0.5)
            except:
                break

        for job in browser.find_elements_by_css_selector(".jobs-search__results-list > li.job-result-card"):
            all_positions.append({
                "Company": "LinkedIn",
                "Title": job.find_element_by_css_selector(".result-card__contents > h3.result-card__title").text,
                "Link": job.find_element_by_css_selector("a.result-card__full-card-link").get_attribute("href")[:job.find_element_by_css_selector("a.result-card__full-card-link").get_attribute("href").index("?")],
                "Location": job.find_element_by_css_selector(".result-card__contents > .result-card__meta > span.job-result-card__location").text
            })
    except:
        print("ERROR: LinkedIn could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from Rockstar Game's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_rockstar_positions(links):
    print("\tScraping for Rockstar Games...", end=" ", flush=True)
    all_positions = []

    for link in links:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("window-size=2880,1800")

        browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
        browser.get(link)

        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#siteBody > div > div > div > div:nth-child(1) > ul > li > ul > li:nth-child(1)")))

            for city in browser.find_elements_by_css_selector("#siteBody > div > div > div > div > ul > li"):
                for job in city.find_elements_by_css_selector("ul > li"):
                    all_positions.append({
                        "Company": "Rockstar Games",
                        "Title": job.find_element_by_css_selector("a").text,
                        "Link": job.find_element_by_css_selector("a").get_attribute("href"),
                        "Location": city.find_element_by_css_selector("a.city > span").text
                    })
        except:
            print("ERROR: Rockstar Games could not be scraped!")

        if len(all_positions) > 0:
            print("Done")

        browser.quit()
        return all_positions


# Scrapes all positions from Spotify's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_spotify_positions(link):
    print("\tScraping for Spotify...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table > tbody.js-jobs-results")))

        while True:
            try:
                if "hidden" not in browser.find_element_by_css_selector("footer").get_attribute("class"):
                    browser.execute_script("arguments[0].click();", browser.find_element_by_css_selector("footer a.btn.js-show-more-jobs"))
                    time.sleep(0.5)
                else:
                    break
            except:
                break

        for job in browser.find_elements_by_css_selector("table > tbody.js-jobs-results > tr"):
            all_positions.append({
                "Company": "Spotify",
                "Title": job.find_element_by_css_selector("td.table-item-title > a > h4").text,
                "Link": job.find_element_by_css_selector("td.table-item-title > a").get_attribute("href"),
                "Location": job.find_element_by_css_selector("td:nth-child(3)").text
            })
    except:
        print("ERROR: Spotify could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from Ubisoft's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_ubisoft_positions(link):
    print("\tScraping for Ubisoft...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=1440,718")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table > tbody")))

        browser.execute_script("window.scrollTo(0, 175);")

        # open 'Choose your area of expertise' dropdown
        browser.find_element_by_css_selector("#sr-widget-search-filters-container > div:nth-child(3) > .k-widget.k-multiselect.k-header").click()
        # select 'Game & Level Design/Creative Direction', 'Online/Web', and 'Programming'
        for area_option in browser.find_elements_by_css_selector("#sr-widget-department-list > div > ul > li"):
            if area_option.text == "Game & Level Design/Creative Direction" or area_option.text == "Online/Web" or area_option.text == "Programming":
                area_option.click()

        # open 'Select a type of contract' dropdown
        browser.find_element_by_css_selector("#sr-widget-search-filters-container > div:nth-child(5) > .k-widget.k-multiselect.k-header").click()
        # select 'Full-time'
        for contract_type in browser.find_elements_by_css_selector("#sr-widget-employment-type-list > div > ul > li"):
            if contract_type.get_attribute("textContent") == "Full-time":
                browser.execute_script("arguments[0].click();", contract_type)

        # open 'Explore opportunities by country' dropdown
        browser.find_element_by_css_selector("#sr-widget-search-filters-container > div:nth-child(7) > .k-widget.k-multiselect.k-header").click()
        # select 'United States'
        for country in browser.find_elements_by_css_selector("#sr-widget-country-list > div > ul > li"):
            if country.text == "United States":
                country.click()

        # click 'Search' button
        browser.find_element_by_css_selector("#sr-widget-search").click()
        time.sleep(0.1)

        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table > tbody")))

            has_more_pages = True
            while has_more_pages:
                for job in browser.find_elements_by_css_selector("table > tbody > tr"):
                    all_positions.append({
                        "Company": "Ubisoft",
                        "Title": job.find_element_by_css_selector("td:nth-child(1) > a").text,
                        "Link": job.find_element_by_css_selector("td:nth-child(1) > a").get_attribute("href"),
                        "Location": job.find_element_by_css_selector("td:nth-child(3) > a").text
                    })

                for nav_button in browser.find_elements_by_css_selector("#sr-widget-job-grid > div.k-pager-wrap > a"):
                    if nav_button.get_attribute("title") == "Go to the next page":
                        if "disabled" in nav_button.get_attribute("class"):
                            has_more_pages = False
                        else:
                            nav_button.click()
        except:
            print("ERROR: Ubisoft could not be scraped!")

    except:
        print("ERROR: Ubisoft could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Scrapes all positions from Zendesk's job board
# Outputs each position with company name, position title, URL, and position location
def scrape_zendesk_positions(link):
    print("\tScraping for Zendesk...", end=" ", flush=True)
    all_positions = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=2880,1800")

    browser = webdriver.Chrome(executable_path='./chromedriver', options=options)
    browser.get(link)

    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".phs-facet-results-block > .phs-jobs-list")))

        # Select Job Category: Engineering & Product
        browser.find_element_by_css_selector(".phs-filter-panels .panel:nth-child(1)").click()
        browser.find_elements_by_css_selector(".phs-filter-panels .panel:nth-child(1) .phs-facet-results > ul > li")[0].click()

        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".phs-facet-results-block > .phs-jobs-list")))

            time.sleep(1)

            # Select Country: United States Of America
            browser.find_element_by_css_selector(".phs-filter-panels .panel:nth-child(2)").click()
            browser.find_elements_by_css_selector(".phs-filter-panels .panel:nth-child(2) .phs-facet-results > ul > li")[0].click()

            try:
                WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".phs-facet-results-block > .phs-jobs-list")))

                time.sleep(1)

                page_count = int(browser.find_element_by_css_selector(".phs-jobs-list-header .phs-header-controls .result-count").text)
                page_count = ((page_count // 10) + 1) if (page_count % 10 > 0) else (page_count // 10)

                for page in range(1, page_count + 1):
                    for job in browser.find_elements_by_css_selector("ul > li.jobs-list-item"):
                        # if multiple locations, open dropdown to get all locations. otherwise, scrape the single location
                        try:
                            job.find_element_by_css_selector(".job-multi-locations > li > button").click()
                            all_positions.append({
                                "Company": "Zendesk",
                                "Title": job.find_element_by_css_selector(".job-title > span").text,
                                "Link": job.find_element_by_css_selector(".information > span > a").get_attribute("href"),
                                "Location": "; ".join([location.text for location in job.find_elements_by_css_selector(".job-multi-locations > li > ul > li.location")])
                            })
                        except:
                            all_positions.append({
                                "Company": "Zendesk",
                                "Title": job.find_element_by_css_selector(".job-title > span").text,
                                "Link": job.find_element_by_css_selector(".information > span > a").get_attribute("href"),
                                "Location": job.find_element_by_css_selector(".job-info .job-location").text[9:]
                            })

                    # move to next page
                    if (page + 1) <= page_count:
                        for i in browser.find_elements_by_css_selector("ul.pagination > li"):
                            if i.find_element_by_css_selector("a").text == str(page + 1):
                                i.find_element_by_css_selector("a").click()
                                break

                    time.sleep(1)
            except:
                print("ERROR: Zendesk could not be scraped! (after selecting Country)")
        except:
            print("ERROR: Zendesk could not be scraped! (after selecting Job Category)")
    except:
        print("ERROR: Zendesk could not be scraped!")

    if len(all_positions) > 0:
        print("Done")

    browser.quit()
    return all_positions


# Strips string of all punctuation so only alphanumeric characters remain
def remove_punctuation(str):
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct = ""

    for char in str:
        if char not in punctuation:
            no_punct += char

    return no_punct


# Filters out any positions that have a position title found in the blacklist
def filter_by_position_title(positions, blacklisted_position_titles):
    filtered_list = []

    for position in positions:
        if (position["Title"].lower() not in [title.lower() for title in blacklisted_position_titles] and
            True not in [position["Title"].lower().startswith(title.lower()) for title in blacklisted_position_titles]):
            filtered_list.append(position)

    return filtered_list


# Filters out any positions with blacklisted keywords found in the title
# If required keywords list isn't empty, only keep positions that contain any required keyword
def filter_by_position_title_keywords(positions, required_keywords, blacklisted_keywords):
    filtered_list = []

    for position in positions:
        if len(required_keywords) > 0:
            if True in [(True if (keyword.lower() in position["Title"].lower()) else False) for keyword in required_keywords]:
                filtered_list.append(position)
        elif True not in [(True if (keyword.lower() in position["Title"].lower()) else False) for keyword in blacklisted_keywords]:
            filtered_list.append(position)

    return filtered_list


# Filters out any positions that are in a location found in the blacklist
# Does not account for when position's location is a list of multiple locations
def filter_by_location(positions, whitelisted_locations, blacklisted_locations):
    filtered_list = []
    unsure_locations = []

    for position in positions:
        if position["Location"] == "" or position["Location"].lower() not in [location.lower() for location in blacklisted_locations]:
            filtered_list.append(position)
        if (position["Location"].lower() not in [location.lower() for location in whitelisted_locations] and
            position["Location"].lower() not in [location.lower() for location in blacklisted_locations] and
            position["Location"] != ""):
            unsure_locations.append(position["Location"])

    if len(unsure_locations) > 0:
        print("Add each location to the whitelist or blacklist:")
        for location in list(set(unsure_locations)):
            print("\t" + location)

    return filtered_list


# Filters out any positions that have already been reviewed
def filter_by_already_seen(positions, already_seen_links):
    filtered_list = []

    for position in positions:
        if position["Link"].lower() not in [link.lower() for link in already_seen_links]:
            filtered_list.append(position)

    return filtered_list


# Export positions into CSV
def export_to_csv(positions):
    f = open("scraped_positions.csv", "w")
    writer = csv.DictWriter(
        f, fieldnames=["Company", "Title", "Link", "Location"])
    writer.writeheader()
    writer.writerows(positions)
    f.close()


def scrape(all_companies, blacklisted_position_titles, required_keywords, blacklisted_keywords, whitelisted_locations, blacklisted_locations, already_seen_links):
    print("Getting all positions on Greenhouse job boards")
    filtered_positions = get_positions_on_greenhouse(all_companies["greenhouse"])

    print("Getting all positions on Lever job boards")
    filtered_positions += get_positions_on_lever(all_companies["lever"])

    print("Getting all positions on Workday job boards")
    filtered_positions += get_positions_on_workday(all_companies["workday"])

    print("Getting all positions on custom job boards")
    filtered_positions += get_positions_using_selenium(all_companies["selenium"])
    filtered_positions += scrape_apple_positions("https://jobs.apple.com/en-us/search?sort=relevance&key=frontend+software%252520engineer&location=united-states-USA&team=apps-and-frameworks-SFTWR-AF")
    filtered_positions += scrape_coda_positions("https://www.linkedin.com/jobs/search/?currentJobId=1343955007&f_C=18274722&locationId=OTHERS.worldwide")
    filtered_positions += scrape_ea_positions("https://ea.gr8people.com/index.gp?method=cappportal.showPortalSearch&sysLayoutId=123&page=1&inp10438=2&inp888=233&inp1810=7&inp1810=4&inp1377=6")
    filtered_positions += scrape_hulu_positions("https://www.hulu.com/jobs/positions")
    filtered_positions += scrape_linkedin_positions("https://www.linkedin.com/jobs/search/?f_C=1337&locationId=OTHERS.worldwide")
    filtered_positions += scrape_rockstar_positions([
        "https://www.rockstargames.com/careers/openings/department/game-code",
        "https://www.rockstargames.com/careers/openings/department/game-design-scripting",
        "https://www.rockstargames.com/careers/openings/department/online-game-services"
    ])
    filtered_positions += scrape_spotify_positions("https://www.spotifyjobs.com/search-jobs/#category=students%2Csoftware-engineering&location=usa")
    filtered_positions += scrape_ubisoft_positions("https://www.ubisoft.com/en-US/careers/search.aspx")
    filtered_positions += scrape_zendesk_positions("https://jobs.zendesk.com/us/en/search-results")

    print("Filtering all positions by position title")
    filtered_positions = filter_by_position_title(filtered_positions, blacklisted_position_titles)
    print("Filtering all positions by position title keywords")
    filtered_positions = filter_by_position_title_keywords(filtered_positions, required_keywords, blacklisted_keywords)
    print("Filtering all positions by location")
    filtered_positions = filter_by_location(filtered_positions, whitelisted_locations, blacklisted_locations)
    print("Filtering all positions by unseen links")
    filtered_positions = filter_by_already_seen(filtered_positions, already_seen_links)

    # Sort positions alphabetically by company name
    print("Sorting all positions alphabetically by company name")
    filtered_positions = sorted(filtered_positions, key=lambda k: k['Company'])

    print("Exporting all positions to CSV file")
    export_to_csv(filtered_positions)

    print("Done!")


def main():
    """
    greenhouse_companies and lever_companies follows the following format:
        {"Company": <Company Name>, "Link": <Optional, End of Link if Differs From Company Name>}

    Example #1: Company name matches link
        Company Name = Google, Greenhouse Link = https://boards.greenhouse.io/google
        {"Company": "Google"}
    Example #2: Company name doesn't match link
        Company Name = Google, Greenhouse Link = https://boards.greenhouse.io/googlejobs
        {"Company": "Google", "Link": "googlejobs"}
    """

    all_companies = {
        "greenhouse": json.load(open('greenhouse_companies.json')),
        "lever": json.load(open('lever_companies.json')),
        "selenium": json.load(open('selenium_companies.json')),
        "workday": json.load(open('workday_companies.json'))
    }
    if len(all_companies["greenhouse"]) > 0 and len(all_companies["lever"]) > 0 and len(all_companies["selenium"]) > 0 and len(all_companies["workday"]) > 0:
        scrape(
            all_companies,
            [line.rstrip('\n') for line in open('blacklisted_position_titles.txt')],
            [],
            [line.rstrip('\n') for line in open('blacklisted_keywords.txt')],
            [line.rstrip('\n') for line in open('whitelisted_locations.txt')],
            [line.rstrip('\n') for line in open('blacklisted_locations.txt')],
            [line.rstrip('\n') for line in open('already_seen_links.txt')]
        )


if __name__ == "__main__":
    main()
