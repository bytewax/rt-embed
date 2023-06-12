from ..objects import WebPage

from bs4 import BeautifulSoup


# recursively get the html from links on the webpage
def recurse_hn(html: str) -> list[WebPage]:
    """
    Get all the links from the html object and request the webpage
    and return them in a list of html bs4 objects.
    This should be used in a flat map"""
    webpages = []
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("tr[class='athing']")
    for lineItem in items:
        ranking = lineItem.select_one("span[class='rank']").text
        link = lineItem.find("span", {"class": "titleline"}).find("a").get("href")
        title = lineItem.find("span", {"class": "titleline"}).text.strip()
        metadata = {
            "source": link,
            "title": title,
            "link": link,
            "ranking": ranking,
        }
        if "item?id=" in link:
            link = f"https://news.ycombinator.com/{link}"
        wp = WebPage(url=link)
        # wp.get_page()
        wp.max_retries = 1
        wp.metadata = metadata
        webpages.append(wp)
    return webpages
