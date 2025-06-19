from bs4 import BeautifulSoup     
import requests                  
import json
import time
import os

def get_year_links(site):
# site = 'https://www.bailii.org/ew/cases/EWCA/Civ/2025/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }

    response = requests.get(site, timeout=3, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    all_case_links = []

    for i in soup.find_all('li'):
        all_case_links.append('https://www.bailii.org' + i.find('a')["href"])

    return all_case_links


def get_case_details(link_list):

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
  }
  case_detail_list = []

  for link in link_list:

    print(f'{link} started')
    case_dict = {}
    case_dict['link'] = link
    case_response = requests.get(link, timeout=3,  headers=headers)
    case_soup = BeautifulSoup(case_response.text, 'html.parser')

    try:
      court = case_soup.find('court').text
      case_dict['court'] = court
    except:
      print(link)
      print(case_soup.find('court'))

    try:
      judges = case_soup.find('panel').text
      case_dict['judges'] = judges
    except:
      print(link)

    try:
      parties = case_soup.find('parties').text.strip()
      case_dict['parties'] = parties
    except:
      print(link)

    try:
      citation = case_soup.find('citation').text
      case_dict['citation'] = citation
    except:
      print(link)

    try:
      case_num = case_soup.find('casenum').text.strip()
      case_dict['case_num'] = case_num
    except:
      print(link)

    try:
      representation = case_soup.find('reps').text.strip()
      case_dict['representation'] = representation
    except:
      print(link)

    if case_soup.find("ol"):
      decision = case_soup.find("ol").find_all(["li", "p", "blockquote"])

      text_dict = {}
      paragraph_number = '0.'
      text_dict['0.0'] = case_soup.find('ol').find('p').text

      for item in decision:
        if item.name == 'blockquote' and item.find_parent('blockquote'):
          continue

        count = 0

        if item.get('value'):
          count = 0
          paragraph_number = (item.get('value'))
        else:
          count+=1
          paragraph_number = paragraph_number.split(".")[0] + f'.{count}'

        paragraph_text = item.get_text(strip=True)

        if paragraph_text:
          text_dict[paragraph_number] = paragraph_text

      paragraph_number = '0.'
      case_dict['text'] = text_dict

      case_detail_list.append(case_dict)
      print(f'{link} done')

  return case_detail_list

def scraper(years):
    base_url = "https://www.bailii.org/ew/cases/EWCA/Civ/{}/"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for year in years:
        print(f"\n===== Processing year: {year} =====")
        year_url = base_url.format(year)

        try:
            links = get_year_links(year_url)
            print(f"Found {len(links)} links for {year}")
        except Exception as e:
            print(f"Failed to get links for {year}: {e}")
            continue

        try:
            details = get_case_details(links)
        except Exception as e:
            print(f"Failed to get case details for {year}: {e}")
            continue

        with open(f"{output_dir}/cases_{year}.json", "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)

        print(f"✅ Year {year} scraping completed and saved.\n")
        time.sleep(2)
  
if __name__ == "__main__":
    years_to_scrape = ["2025"] 
    scraper(years_to_scrape)