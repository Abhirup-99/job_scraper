import csv, json, requests, string
from bs4 import BeautifulSoup


# Scrapes all positions from each greenhouse job board in input list
# Outputs each position with company name, position title, URL, and position location
def get_positions_on_greenhouse(job_boards):
    root_link = "https://boards.greenhouse.io/"
    all_positions = []

    for job_board in job_boards:
        page = requests.get(root_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(root_link + job_board["Link"])
        sections = BeautifulSoup(page.text, 'html.parser').find_all("section", {"class": "level-0"})

        if len(sections) == 0:
            print("ERROR:", job_board["Company"], "could not be scraped!")

        for section in sections:
            for position in section.find_all("div", {"class": "opening"}):
                all_positions.append({
                    "Company": job_board["Company"],
                    "Title": position.find("a").getText().strip(),
                    "Link": root_link[:-1] + position.find("a")['href'],
                    "Location": position.find("span", {"class": "location"}).getText().strip()
                })

    return all_positions


# Scrapes all positions from each lever job board in input list
# Outputs each position with company name, position title, URL, and position location
def get_positions_on_lever(job_boards):
    root_link = "https://jobs.lever.co/"
    all_positions = []

    for job_board in job_boards:
        page = requests.get(root_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(root_link + job_board["Link"])
        positions = BeautifulSoup(page.text, 'html.parser').find_all("div", {"class": "posting"})

        if len(positions) == 0:
            print("ERROR:", job_board["Company"], "could not be scraped!")

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
        if position["Location"].lower() not in [location.lower() for location in blacklisted_locations]:
            filtered_list.append(position)
        if (position["Location"].lower() not in [location.lower() for location in whitelisted_locations] and
            position["Location"].lower() not in [location.lower() for location in blacklisted_locations]):
            unsure_locations.append(position["Location"])

    if len(unsure_locations) > 0:
        print("Add each location to the whitelist or blacklist:")
        for location in list(set(unsure_locations)):
            print("\t" + "\"" + location + "\",")

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


def scrape(greenhouse_companies, lever_companies, blacklisted_position_titles, required_keywords, blacklisted_keywords, whitelisted_locations, blacklisted_locations, already_seen_links):
    greenhouse_positions = get_positions_on_greenhouse(greenhouse_companies)
    lever_positions = get_positions_on_lever(lever_companies)

    filtered_positions = greenhouse_positions + lever_positions
    filtered_positions = filter_by_position_title(filtered_positions, blacklisted_position_titles)
    filtered_positions = filter_by_position_title_keywords(filtered_positions, required_keywords, blacklisted_keywords)
    filtered_positions = filter_by_location(filtered_positions, whitelisted_locations, blacklisted_locations)
    filtered_positions = filter_by_already_seen(filtered_positions, already_seen_links)

    # Sort positions alphabetically by company name
    filtered_positions = sorted(filtered_positions, key=lambda k: k['Company'])

    export_to_csv(filtered_positions)


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

    greenhouse_companies = json.load(open('greenhouse_companies.json'))
    lever_companies = json.load(open('lever_companies.json'))
    blacklisted_position_titles = [line.rstrip('\n') for line in open('blacklisted_position_titles.txt')]
    whitelisted_locations = [line.rstrip('\n') for line in open('whitelisted_locations.txt')]
    blacklisted_locations = [line.rstrip('\n') for line in open('blacklisted_locations.txt')]
    required_keywords = []
    blacklisted_keywords = [line.rstrip('\n') for line in open('blacklisted_keywords.txt')]
    already_seen_links = [line.rstrip('\n') for line in open('already_seen_links.txt')]

    if len(greenhouse_companies) > 0 and len(lever_companies):
        scrape(greenhouse_companies, lever_companies, blacklisted_position_titles, required_keywords, blacklisted_keywords, whitelisted_locations, blacklisted_locations, already_seen_links)


if __name__ == "__main__":
    main()
