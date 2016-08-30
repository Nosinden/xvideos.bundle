# setup title and prefix
TITLE = 'xVideos'
PREFIX = '/video/xvideos'

# setup default icon/art and base URL
ART = 'art-default.jpg'
ICON = 'icon-default.png'
BASE_URL = 'http://www.xvideos.com'

# setup regex, similar to re.compile
RE_LIST_ID = Regex('listId: "(.+?)", pagesConfig: ')
RE_CONTENT_ID = Regex('CONTENT_ID = "(.+?)";')
THUMB_REG = Regex('img src="(http:.*)" id')

###################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)

    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR  # Set channel and HTTP cache time to 1 hour

###################################################################################################
# This tells Plex how to list you in the available channels and what type of channels this is
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    """This function is the first and main menu for you channel."""

    # You have to open an object container to produce the icons you want to appear on this page.
    oc = ObjectContainer()
    main_list = [('New Videos', ''), ('Best Videos', '/best'), ('Pornstars', '/pornstars')]
    for pt, h in main_list:
        oc.add(DirectoryObject(
            key=Callback(ShowHTML, pTitle=pt, href=h),
            title=pt, thumb=Callback(GetThumb, url=BASE_URL)))
    oc.add(DirectoryObject(
        key=Callback(ShowHTML, pTitle="Pornstars", href='/channels'),
        title="Channels", thumb=Callback(GetThumb, url=BASE_URL)))

    oc.add(InputDirectoryObject(key=Callback(Search), title='Search Videos', prompt='Search Videos'))

    return oc

###################################################################################################
@route(PREFIX + '/showhtml')
def ShowHTML(pTitle, href):
    """This function is an example of parsing data from a html page"""

    oc = ObjectContainer(title2=pTitle)

    href = href if href else ''
    html = HTML.ElementFromURL(BASE_URL + href)

    if '/pornstars-click/' in href:
        href = '/profiles/' + href.rsplit('/', 1)[1]
    url = BASE_URL + href

    xvideosBest = "thumb-block "
    if (len(html.xpath('//div[@class="thumbBlock"]')) > 0):
        xvideosBest = "thumbBlock"

    if (len(html.xpath('//title//text()')) > 0):
        if 'Pornstar page' in html.xpath('//title//text()')[0]:
            url = url + '/pornstar_videos/0/0'
            html = HTML.ElementFromURL(url)
        elif 'Channel page' in html.xpath('//title//text()')[0]:
            url = url + '/uploads/0/0'
            html = HTML.ElementFromURL(url)

    for video in html.xpath('//div[@class="%s"]' %xvideosBest):
        try:
            if '/profiles/' not in url and '/pornstars-click' not in url:
                if (len(video.xpath('./div/div/a//@href')) == 0):
                    oc.add(VideoClipObject(
                        url=BASE_URL + video.xpath('./p/a//@href')[0],
                        title=video.xpath('./p/a//text()')[0],
                        thumb=THUMB_REG.search(video.xpath('./div/div/script//text()')[0]).group(1)
                        ))
                else:
                    vhref = video.xpath('./p/a//@href')[0]
                    vtitle = video.xpath('./p/a//text()')[0]
                    oc.add(DirectoryObject(
                        key=Callback(ShowHTML, href=vhref, pTitle=vtitle),
                        title=vtitle, thumb=THUMB_REG.search(video.xpath('./div/div/a/script//text()')[0]).group(1)
                        ))
            else:
                oc.add(VideoClipObject(
                    url=BASE_URL + video.xpath('./div/p/a//@href')[0],
                    title=video.xpath('./div/p/a//text()')[0],
                    thumb=video.xpath('./div/div/a/img//@src')[0]
                    ))
        except:
            Log.Warn('nothing')

    # setup nextURL
    try:
        nextURL = None
        if html.xpath('//li/a[@data-page][text()="Next"]'):
            next_page = int(html.xpath('//li/a[text()="Next"]/@data-page')[0])
            nextURL = '/{}/{}'.format(url.split('/', 3)[3].rsplit('/', 1)[0], next_page)
        elif html.xpath('//li/a[@class="no-page"][text()="Next"]'):
            nextURL = html.xpath('//li/a[@class="no-page"][text()="Next"]/@href')[0]
        elif html.xpath('//div[contains(@class,"pagination")]//a[@class="active"]/../following-sibling::li/a/@href'):
            nextURL = html.xpath("//div[contains(@class,'pagination')]/ul/li/a[@class='active']/../following-sibling::li/a/@href")[0]

        if nextURL:
            next_page_num = nextURL.split('=')[-1] if '&' in nextURL else nextURL.split('/')[-1]
            next_page_num = next_page_num if next_page_num else nextURL.split('/')[-2]
            #Log(u"next page number = '{}'".format(next_page_num))
            oc.add(NextPageObject(
                key=Callback(ShowHTML, href=nextURL, pTitle='Page ' + next_page_num),
                title="More ..."))
    except:
        Log.Exception("Cannot find next page")
    # it will loop through and return the values for all items in the page
    return oc

###################################################################################################
@route(PREFIX + '/getthumb')
def GetThumb(url):
    """This is a function to pull the thumb from a the head of a page"""
    try:
        html = HTML.ElementFromURL(url)
        thumb = html.xpath("//head//meta[@property='og:image']//@content")[0]
        if not thumb.startswith('http://'):
            thumb = 'http://' + thumb
    except Exception, e:
        Log.Warn(u"Cannot find thumb for '{}'. Returning default icon.".format(url))
        Log.Error(str(e))
        thumb = R(ICON)
    return Redirect(thumb)

###################################################################################################
@route(PREFIX + '/Search')
def Search(query="test"):
    search = String.Quote(query, usePlus=True)
    return ShowHTML(pTitle="Search xvideos", href="/?k=" + search)
