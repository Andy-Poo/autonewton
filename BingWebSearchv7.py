#Copyright (c) Microsoft Corporation. All rights reserved.
#Licensed under the MIT License.

# -*- coding: utf-8 -*-

#import http.client, urllib.parse, json
import httplib, json
from urllib import quote_plus

# **********************************************
# *** Update or verify the following values. ***
# **********************************************

# Replace the subscriptionKey string value with your valid subscription key.
#subscriptionKey = "somehexadecimalstring"
import os
subscriptionKey = os.environ.get('BING_SEARCH_KEY')


# Verify the endpoint URI.  At this writing, only one endpoint is used for Bing
# search APIs.  In the future, regional endpoints may be available.  If you
# encounter unexpected authorization errors, double-check this value against
# the endpoint for your Bing Web search instance in your Azure dashboard.
host = "api.cognitive.microsoft.com"
path = "/bing/v7.0/search"

term = "Microsoft Cognitive Services"

def BingWebSearch(search):
    "Performs a Bing Web search and returns the results."

    headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
    #conn = http.client.HTTPSConnection(host)
    conn = httplib.HTTPSConnection(host)
    #query = urlparse.quote(search)
    query = quote_plus(search)
    conn.request("GET", path + "?q=" + query, headers=headers)
    response = conn.getresponse()
    headers = [k + ": " + v for (k, v) in response.getheaders()
                   if k.startswith("BingAPIs-") or k.startswith("X-MSEdge-")]
    return headers, response.read().decode("utf8")

def Bing(term, youtube=False):
    headers, result = BingWebSearch(term)
    data = json.loads(result)
    #import pprint
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(data)
    try:
        if youtube and 'images' in data:
            page = data['images']
        else:
            page = data['webPages']
    except Exception as e:
        print 'Bing: Error:', e
        return ''
    #import pprint
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(page)
    
    value = page['value']
    result = ''
    count = 0
    if youtube:
        for v in value:
            #url = v['contentUrl']
            if 'hostPageUrl' in v:
                url = v['hostPageUrl']
            elif 'displayUrl' in v:
                url = v['displayUrl']
            if 'youtube' in url:
                count += 1
                if count <= 3:
                    result += '\n' + url
    else:
        for v in value[:3]:
            url = v['url']
            snippet = v['snippet']
            result += '\n' + '='*10 + '\n%s\n%s' % (url, snippet)
    return result

