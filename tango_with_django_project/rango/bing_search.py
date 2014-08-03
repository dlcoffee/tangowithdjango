import json
import urllib, urllib2
from keys import BING_API_KEY


def run_query(search_terms):
    '''
    1.  prepares for connecting to Bing by preparing the URL that
        we will be requesting
    2.  prepares authentication, making use of the Bing API key
    3.  connect to API through the 'urllib2.urlopen(search_url') command
        the results are returned as a string
    4.  string is parsed into a python dictionary using the 'json' package
    5.  loop trhough each 'result' and populate the results dictionary
    '''
    # specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    # specify how many results we wish to be returned per page
    # offset specifies where in the results list to start from
    # with results_per_page = 10 and offset = 11, we would start on page 2
    results_per_page = 10
    offset = 0

    # wrap quotes around our query terms as required by the Bing API
    # the query we will use is stored with the variable `query`
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # construct the latter part of the request URL
    # sets the format of the response to JSON and sets other properties
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(            
        root_url,
        source,
        results_per_page,
        offset,
        query)

    # set up auth with Bing servers
    # the username MUST be a blank string
    username = ''
    bing_api_key = BING_API_KEY

    # create a "password manager" which handles auth for us
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)

    # create our results list
    results = []


    try:
        # prepare for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)


        # connect to the server and read the response generated
        response = urllib2.urlopen(search_url).read()


        # convert the string response to a dictionary object
        json_response = json.loads(response)

        # loop through each page returned, and populate the `results` list
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})

    # catch a URLError exception - something went wrong with connecting
    except urllib2.URLError, e:
        print "Error when querying the Bing API: ", e

    return results
        



def main():
    query = raw_input("Enter a query: ")
    results = run_query(query)

    rank = 1

    for result in results:
        print "Rank {0}".format(rank)
        print result['title']
        print result['link']
        print

        rank += 1

if __name__ == '__main__':
    main()
