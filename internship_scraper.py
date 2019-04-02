import requests, csv, string
from bs4 import BeautifulSoup


def get_greenhouse_positions(gh_link, gh_boards):
    all_positions = []

    for job_board in gh_boards:
        page = requests.get(gh_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(gh_link + job_board["Link"])
        sections = BeautifulSoup(page.text, 'html.parser').find_all("section", {"class": "level-0"})

        for section in sections:
            for position in section.find_all("div", {"class": "opening"}):
                all_positions.append({
                    "Company": job_board["Company"],
                    "Title": position.find("a").getText().strip(),
                    "Link": gh_link[:-1] + position.find("a")['href'],
                    "Location": position.find("span", {"class": "location"}).getText().strip()
                })

    return all_positions


def get_lever_positions(l_link, l_boards):
    all_positions = []

    for job_board in l_boards:
        page = requests.get(l_link + job_board["Company"].replace(" ", "").lower()) if "Link" not in job_board else requests.get(l_link + job_board["Link"])
        positions = BeautifulSoup(page.text, 'html.parser').find_all("div", {"class": "posting"})

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


def remove_punctuation(str):
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct = ""

    for char in str:
        if char not in punctuation:
            no_punct += char

    return no_punct


def filter_positions(positions):
    no_locations = ["Toronto", "Germany", "Estonia", "Japan", "Canada", "Australia", "New Zealand", "United Kingdom", "Denmark", "Milan", "Turkey", "Singapore", "Amsterdam", "London", "Paris", "Sao Paulo", "Copenhagen"]
    new_positions = []

    for position in positions:
        title = remove_punctuation(position["Title"].lower())
        if ("intern" in title.split() or "coop" in title or "univ" in title) and ("summer 2019" not in title) and ("mba" not in title) and not [False for no_loc in no_locations if no_loc.lower() in position["Location"].lower()]:
            new_positions.append(position)

    return new_positions


def main():
    gh_positions = get_greenhouse_positions("https://boards.greenhouse.io/", [
        {"Company": "Amplitude"},
        {"Company": "Asana"},
        {"Company": "Box", "Link": "boxinc"},
        {"Company": "DoorDash"},
        {"Company": "Foursquare", "Link": "foursquare26"},
        {"Company": "Flexport"},
        {"Company": "Flyhomes"},
        {"Company": "Instacart"},
        {"Company": "Intercom"},
        {"Company": "MailChimp"},
        {"Company": "Managed by Q"},
        {"Company": "Mozilla"},
        {"Company": "Patreon"},
        {"Company": "Postmates"},
        {"Company": "Redbooth"},
        {"Company": "Robinhood"},
        {"Company": "Samsara"},
        {"Company": "SeatGeek"},
        {"Company": "Sonder"},
        {"Company": "Splash"},
        {"Company": "Thumbtack"},
        {"Company": "Twilio"},
        {"Company": "Uptake"},
        {"Company": "Vimeo", "Link": "vimeointernships"}
    ])
    l_positions = get_lever_positions("https://jobs.lever.co/", [
        {"Company": "Affinity"},
        {"Company": "Affirm"},
        {"Company": "Algolia"},
        {"Company": "Atlassian"},
        {"Company": "Atrium"},
        {"Company": "Bird"},
        {"Company": "Bolt"},
        {"Company": "Brex"},
        {"Company": "BuildingConnected"},
        {"Company": "Carta"},
        {"Company": "Comma"},
        {"Company": "Ditto"},
        {"Company": "Envoy"},
        {"Company": "Even", "Link": "teameven"},
        {"Company": "Figma"},
        {"Company": "Houseparty"},
        {"Company": "Houzz"},
        {"Company": "IFTTT"},
        {"Company": "Karat"},
        {"Company": "Lattice", "Link": "latticehq"},
        {"Company": "Lever"},
        {"Company": "Medium"},
        {"Company": "Opendoor"},
        {"Company": "Palantir"},
        {"Company": "Plaid"},
        {"Company": "Quantcast"},
        {"Company": "Spoke", "Link": "askspoke"},
        {"Company": "Twitch"},
        {"Company": "Udemy"},
        {"Company": "Wealthfront"},
        {"Company": "Y Combinator"},
        {"Company": "Yelp"},
        {"Company": "Zendesk"}
    ])

    blacklisted_positions = [
        "Graphic Design Intern",
        "Recruiting Intern",
        "University Recruit",
        "People Team Intern",
        "Marketing Operations Intern",
        "Government Affairs Intern",
        "Sales Intern -",
        "Legal Intern",
        "Community Intern -",
        "Billing Operations Intern",
        "Social Media Intern",
        "Business Operations Intern",
        "Financial Planning and Analysis Intern",
        "Twilio Intern Program- Sales Intern",
        "SEO Intern",
        "Regional Marketing Campaigns Intern",
        "2019 Management",
        "2019 Security",
        "2019 University Business",
        "2019 University Security",
        "2019 University Site Reliability"
    ]

    all_positions = sorted(filter_positions(gh_positions + l_positions), key=lambda k: k['Company'])
    all_positions = [x for x in all_positions if x["Title"] not in blacklisted_positions and not any(x["Title"].startswith(bl_p) for bl_p in blacklisted_positions)]

    f = open("intern_positions.csv", "w")
    writer = csv.DictWriter(
        f, fieldnames=["Company", "Title", "Link", "Location"])
    writer.writeheader()
    writer.writerows(all_positions)
    f.close()


if __name__ == "__main__":
    main()
