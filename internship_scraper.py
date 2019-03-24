import requests, csv, string
from bs4 import BeautifulSoup


def get_greenhouse_positions(gh_link, gh_boards):
    all_positions = []

    for job_board in gh_boards:
        page = requests.get(gh_link + job_board["Link"])
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
        page = requests.get(l_link + job_board["Link"])
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
        if ("intern" in title.split() or "co-op" in title or "univ" in title) and ("summer 2019" not in title) and not [False for no_loc in no_locations if no_loc.lower() in position["Location"].lower()]:
            new_positions.append(position)

    return new_positions


def main():
    gh_positions = get_greenhouse_positions("https://boards.greenhouse.io/", [
        {"Company": "Amplitude", "Link": "amplitude"},
        {"Company": "Asana", "Link": "asana"},
        {"Company": "Box", "Link": "boxinc"},
        {"Company": "DoorDash", "Link": "doordash"},
        {"Company": "Foursquare", "Link": "foursquare26"},
        {"Company": "Flexport", "Link": "flexport"},
        {"Company": "Flyhomes", "Link": "flyhomes"},
        {"Company": "Instacart", "Link": "instacart"},
        {"Company": "Intercom", "Link": "intercom"},
        {"Company": "MailChimp", "Link": "mailchimp"},
        {"Company": "Managed by Q", "Link": "managedbyq"},
        {"Company": "Mozilla", "Link": "mozilla"},
        {"Company": "Patreon", "Link": "patreon"},
        {"Company": "Redbooth", "Link": "redbooth"},
        {"Company": "Robinhood", "Link": "robinhood"},
        {"Company": "Samsara", "Link": "samsara"},
        {"Company": "SeatGeek", "Link": "seatgeek"},
        {"Company": "Sonder", "Link": "sonder"},
        {"Company": "Splash", "Link": "splash"},
        {"Company": "Thumbtack", "Link": "thumbtack"},
        {"Company": "Twilio", "Link": "twilio"},
        {"Company": "Vimeo", "Link": "vimeointernships"}
    ])
    l_positions = get_lever_positions("https://jobs.lever.co/", [
        {"Company": "Affinity", "Link": "affinity"},
        {"Company": "Affirm", "Link": "affirm"},
        {"Company": "Algolia", "Link": "algolia"},
        {"Company": "Atlassian", "Link": "atlassian"},
        {"Company": "Atrium", "Link": "atrium"},
        {"Company": "Bird", "Link": "bird"},
        {"Company": "Bolt", "Link": "bolt"},
        {"Company": "Brex", "Link": "brex"},
        {"Company": "BuildingConnected", "Link": "buildingconnected"},
        {"Company": "Carta", "Link": "carta"},
        {"Company": "Comma", "Link": "comma"},
        {"Company": "Ditto", "Link": "ditto"},
        {"Company": "Envoy", "Link": "envoy"},
        {"Company": "Even", "Link": "teameven"},
        {"Company": "Figma", "Link": "figma"},
        {"Company": "Houseparty", "Link": "houseparty"},
        {"Company": "Houzz", "Link": "houzz"},
        {"Company": "IFTTT", "Link": "ifttt"},
        {"Company": "Karat", "Link": "karat"},
        {"Company": "Lattice", "Link": "latticehq"},
        {"Company": "Lever", "Link": "lever"},
        {"Company": "Medium", "Link": "medium"},
        {"Company": "Opendoor", "Link": "opendoor"},
        {"Company": "Palantir", "Link": "palantir"},
        {"Company": "Plaid", "Link": "plaid"},
        {"Company": "Quantcast", "Link": "quantcast"},
        {"Company": "Spoke", "Link": "askspoke"},
        {"Company": "Twitch", "Link": "twitch"},
        {"Company": "Udemy", "Link": "udemy"},
        {"Company": "Wealthfront", "Link": "wealthfront"},
        {"Company": "Y Combinator", "Link": "ycombinator"},
        {"Company": "Yelp", "Link": "yelp"},
        {"Company": "Zendesk", "Link": "zendesk"}
    ])

    all_positions = filter_positions(gh_positions + l_positions)

    f = open("intern_positions.csv", "w")
    writer = csv.DictWriter(
        f, fieldnames=["Company", "Title", "Link", "Location"])
    writer.writeheader()
    writer.writerows(all_positions)
    f.close()


if __name__ == "__main__":
    main()
