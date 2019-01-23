import duckduckgo

# diagnostic logging
debug = False

def DuckWebSearch(search, youtube=False):
    """Performs a DuckDuckGo Web search and returns the results.

    youtube : bool
        True if doing a Youtube lookup

    Returns:
        str : the result of the web search
    """
    if debug: print 'DuckWebSearch: search=', search
    if debug: print 'DuckWebSearch: youtube=', youtube
    if youtube:
        #search = 'youtube' + ' ' + search
        args = {'ia': 'videos'}
    else:
        args = {'ia': 'web'}
    response = duckduckgo.query(search, **args)
    result = ''
    json = response.json
    keys = sorted(json.keys())
    #result += str(keys)
    if 'Image' in keys:
        result += '\n' + json['Image']
    if 'AbstractURL' in keys:
        result += '\n' + json['AbstractURL']
    if 'Abstract' in keys:
        result += '\n' + json['Abstract']
    #for key in keys:
    #    result += '\n%s: %s' % (key, json[key])
    return result.strip()

def Duck(query, youtube=False):
    """Performs a DuckDuckGo Web search and returns the results.

    query : str
        the string to search for.
    youtube : bool
        True if doing a Youtube lookup

    Returns:
        str : the result of the web search
    """
    result = DuckWebSearch(query, youtube=youtube)
    if debug: print 'Duck: result:', result
    #data = json.loads(result)
    #import pprint
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(data)
    return result

