from requests import *
from bs4 import BeautifulSoup
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
    leveldomain = domain + (baseurl[:baseurl.rindex(r"/")])[baseurl.index(r"/",8):]
    print(f"Base domain: {domain}\nLevel domain: {leveldomain}")
    links = list()
    links.append(baseurl)

    for url in links:
        print(f"Crawling {url}")
        try:
            response = get(url)
        except:
            print(f"HTTP connection to {url} has failed, might be an invalid url")
            continue
        doc = BeautifulSoup(response.text,"lxml")
        for finding in doc.find_all("a"):
            if not finding.has_attr("href"):
                continue
            parsedUrl = finding["href"]
            if parsedUrl=="" or parsedUrl[0] == "#":
                continue
            if (re.match("http",parsedUrl) or re.match(r"//",parsedUrl)) and not re.search(leveldomain,parsedUrl):
                #print(f"New URL found: {parsedUrl} but its an out or upper sider")
                continue
            if "#" in parsedUrl:
                parsedUrl = parsedUrl[:parsedUrl.rindex("#")]
            if "?" in parsedUrl:
                parsedUrl = parsedUrl[:parsedUrl.rindex("?")]
            if not re.search(domain,parsedUrl) or not re.match(r"//",parsedUrl):
                parsedUrl = evaluateDoubleDotNotation(url,parsedUrl)
            if parsedUrl in links or parsedUrl[-3:] in ("pdf","jpg","jpeg","png") or not re.search(leveldomain,parsedUrl):
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
        currNum = 1
        doc = BeautifulSoup(response.text,"lxml")
        for finding in doc.find_all("table"):
            name = str()
            if finding.has_attr("id"):
                print(f"Table found with id {(finding['id'])}")
                name = " ".join((url, finding['id']))
            else:
                print("Table found. Since it has no id, it is gonna be called: {}".format(currNum))
                newurl = url.replace("/","_").replace(":","")
                name = f"{newurl} {currNum}.csv"
                currNum = currNum + 1
            with open(name,"w",encoding="utf-8") as file:
                for row in finding("tr"):
                    for cell in row("td"):
                        if cell.string is not None:
                            file.write(cell.string)
                        file.write(",")
                    file.write("\n")
            

if __name__ == "__main__":
    """ if len(argv) < 3:
        print("Not enough arguments\nExiting....")
        exit() """
    main()