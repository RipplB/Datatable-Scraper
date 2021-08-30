from requests import *
from sys import argv
import re

def calculateDomain(url: str) -> str:
    if re.match(r"http",url):
        url = url[url.index(":") + 3:]
    if re.match(r"www",url):
        url = url[4:]
    try:
        return url[:url.index("/")]
    except ValueError:
        return url

def evaluateDoubleDotNotation(url: str,doubledot: str) -> str:
    result = url[:url.rindex("/")+1]
    if doubledot[0] == '/' and doubledot[1] != '/':
        return "http://" + calculateDomain(url) + "/" + doubledot[1:]
    while '/' in doubledot:
        if doubledot[0] != '.':
            result = result + doubledot[:doubledot.index('/') + 1]
            doubledot = doubledot[doubledot.index('/') + 1:]
            continue
        if doubledot[1] == '/':
            doubledot= doubledot[2:]
            continue
        if doubledot[1] == '.' and doubledot[2] == '/':
            result = result[:-1]
            result = result[:result.rindex("/")+1]
            doubledot = doubledot[3:]
        else:
            raise ValueError(f"Invalid dotted notated value. Base url:{url}\nResult on error:{result}\nDotted on error:{doubledot}")
    return result + doubledot

def tagToDictionary(tag:str)->dict:
    #return {key:value for word in tag[:-1].split(" ")[1:] for key,value in word.split("=")}
    try:
        return dict([word.partition("=")[::2] for word in tag[:-1].split(" ")[1:]])
    except ValueError:
        raise ValueError(f"tagToDict errored, tag was: {tag}")
def main():
    baseurl = argv[1]
    #pattern = argv[2]
    domain = calculateDomain(baseurl)
    leveldomain = domain + (baseurl[:baseurl.rindex(r"/")])[baseurl.index(r"/"):]
    print(f"Base domain: {domain}")
    links = list()
    links.append(baseurl)

    for url in links:
        print(f"Crawling {url}")
        try:
            response = get(url)
        except:
            #print(f"HTTP connection to {url} has failed, might be an invalid url")
            continue
        for finding in re.finditer(r"<a.*href=.*?>",response.text):
            parsedUrl = finding.group()
            parsedUrl = parsedUrl[:parsedUrl.index(">")+1] #because re is sometimes greedy even tho it was told not to be
            attribs = tagToDictionary(parsedUrl)
            if "href" not in attribs.keys():
                continue
            parsedUrl = attribs["href"].strip('"')
            if parsedUrl=="" or parsedUrl[0] == "#":
                continue
            if (re.match("http",parsedUrl) or re.match(r"//",parsedUrl)) and not re.search(leveldomain,parsedUrl):
                #print(f"New URL found: {parsedUrl} but its an out or upper sider")
                continue
            if "#" in parsedUrl:
                parsedUrl = parsedUrl[:parsedUrl.rindex("#")]
            if not re.search(domain,parsedUrl) or not re.match(r"//",parsedUrl):
                parsedUrl = evaluateDoubleDotNotation(url,parsedUrl)
            if parsedUrl in links or parsedUrl[-3:] in ("pdf","jpg","jpeg","png"):
                continue
            print(f"New URL found and added to the list: {parsedUrl}")
            links.append(parsedUrl)
    print(f"\n\nCrawling complete, found {len(links)} suitable urls.\nBeginning to fetch data.....\n")

    for url in links:
        print(f"Looking for data on {url}")
        try:
            response = get(url)
        except:
            print(f"HTTP connection to {url} has failed, might be an invalid url")
            continue
        fileOName = str()
        for finding in re.finditer(r"<table.*>.*</table>",response.text):
            openingtag = re.match("<.*>",finding.group()).group()
            attribs = tagToDictionary(openingtag)
            if "id" in attribs.keys():
                print(f"Table found with id {(attribs['id'])}")

if __name__ == "__main__":
    """ if len(argv) < 3:
        print("Not enough arguments\nExiting....")
        exit() """
    main()