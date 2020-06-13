# if error, use pip to install beautisoup4
from bs4 import BeautifulSoup
import re
import requests
import json
import urllib.parse
from os import system, name

##
# Define variable
##
tag_api_url = 'https://mo7dwh9y8c-2.algolianet.com/1/indexes/*/queries'
stories_api_url = 'https://mo7dwh9y8c-3.algolianet.com/1/indexes/*/queries'
detail_stories_url = 'https://hackernoon.com/_next/data/NCUGwUUyLGGjQ4vHrpM3K/' # Change in each hours
get_parameters = {
    'x-algolia-agent': 'Algolia for JavaScript (4.1.0); Browser (lite); JS Helper (3.1.1); react (16.13.1); react-instantsearch (6.4.0)',
    'x-algolia-api-key': 'e0088941fa8f9754226b97fa87a7c340',
    'x-algolia-application-id': 'MO7DWH9Y8C'
}

##
# Define function
##
def clear():
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear') 


def generatePostData(isTag=True, isFacet=False, hitsPerPage=10, pageIndex=0, tagName=''):
    indexName = 'tags'
    if (True == isFacet):
        indexName = 'stories'
    params = {
        'highlightPreTag': '<Cais-highlight-0000000000>',
        'highlightPostTag': '</ais-highlight-0000000000>',
        'hitsPerPage': hitsPerPage,
        'query': '',
        'page': pageIndex,
        'facets': '[]',
        'tagFilters': ''
    }
    if (True == isFacet & 0 < tagName.len()):
        params['facetFilters'] = '["tags:' + tagName + '"]'
    return {
        'indexName': indexName,
        'params': urllib.parse.urlencode(params)
    }


def getTags(page=0, limit=100):
    query = urllib.parse.urlencode(get_parameters)
    raw_data = '{"requests":[' + json.dumps(generatePostData(
        isTag=True, isFacet=False, hitsPerPage=limit, pageIndex=page)) + ']}'
    response = requests.post(tag_api_url + '?' + query, data=raw_data)
    if (response.status_code == 400):
        return []
    tags = json.loads(response._content)['results'][0]['hits']
    result = {}
    index = 0
    for tag in tags:
        result[index] = tag['slug']
        index = index + 1
    return result


def getStories(page=0, limit=10, tag=''):
    query = urllib.parse.urlencode(get_parameters)
    raw_data = '{"requests":[' + json.dumps(generatePostData(
        isTag=False, isFacet=True, hitsPerPage=limit, pageIndex=page, tagName=tag)) + ']}'
    response = requests.post(stories_api_url + '?' + query, data=raw_data)
    if (response.status_code == 400):
        return {}
    stories = json.loads(response._content)['results'][0]['hits']
    result = {}
    for story in stories:
        result.update({
            story['slug']: {
                'title': story['title'],
                'author': story['profile']['displayName'],
                'createdAt': story['createdAt'],
                'submittedAt': story['submittedAt'],
                'publishedAt': story['publishedAt'],
                'tags': story['tags']
            }
        })
    return result


def removeDuplicateStory(stories):
    keys = list(set(list(stories.keys())))
    result = {}
    for key in keys:
        result[key] = stories[key]
    return result

def getDetailStory(url):
    response = requests.get(detail_stories_url + url + '.json')
    if (response.status_code == 400):
        return {}
    result = json.loads(response._content)['pageProps']['data']['markup']
    return result


def getLinksInStory(htmlSource):
    soup = BeautifulSoup(htmlSource, "html.parser")
    result = []
    for link in soup.findAll('a'):
        result.append(link.get('href'))
    return result


def getImagesInStory(htmlSource):
    soup = BeautifulSoup(htmlSource, "html.parser")
    result = []
    for img in soup.findAll('img'):
        result.append(img.get('src'))
    return result



def cleanHtmlTagInStory(htmlSource):
    soup = BeautifulSoup(htmlSource, 'lxml')
    result = ''
    for link in soup.select('div.paragraph'):
        result = result + ' ' + link.getText()
    return result


##
# Execute code
##
result = {}
tags = getTags(page=0, limit=5)
index = 0
for t in tags:
    stories = removeDuplicateStory(getStories(page=0, limit=5, tag=t))
    for url, value in stories.items():
        clear()
        print('Đã crawl được', index + 1, '/', 2500 ,'bài viết')
        detail = getDetailStory(url)
        links = getLinksInStory(detail)
        imgs = getImagesInStory(detail)
        source = cleanHtmlTagInStory(detail)
        value.update({'links': links, 'imgs': imgs, 'content': source})
        result.update({index: value})
        index = index + 1


##
# Save data into file
##
clear()
print('Saving data to file: hackernoon_data.json')
json_data = json.dumps(result)
file = open("hackernoon_data.json", "w")
file.write(json_data)
print('Save data to file success!')
file.close()
