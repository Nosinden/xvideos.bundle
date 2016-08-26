
TITLE    = 'xVideos'
PREFIX   = '/video/xvideos'


ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

WebsiteURL = 'http://www.xvideos.com'
http = 'http:'
# This variable it to make an id below work as a url link
WebsiteEpURL = 'http://www.xvideos.com/'

RE_LIST_ID = Regex('listId: "(.+?)", pagesConfig: ')
RE_CONTENT_ID = Regex('CONTENT_ID = "(.+?)";')
THUMB_REG = Regex('img src="(http:.*)" id')

  
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  EpisodeObject.thumb = R(ICON)
  EpisodeObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

###################################################################################################
# This tells Plex how to list you in the available channels and what type of channels this is 
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

# This function is the first and main menu for you channel.

 
def MainMenu():

# You have to open an object container to produce the icons you want to appear on this page. 
  oc = ObjectContainer()

  oc.add(DirectoryObject(key=Callback(ShowHTML, pTitle="New Videos", url='http://www.xvideos.com'), title="New Videos", thumb=GetThumb(url='http://www.xvideos.com')))
  oc.add(DirectoryObject(key=Callback(ShowHTML, pTitle="Best Videos", url='http://www.xvideos.com/best'), title="Best Videos", thumb=GetThumb(url='http://www.xvideos.com')))
  oc.add(DirectoryObject(key=Callback(ShowHTML, pTitle="Pornstars", url='http://www.xvideos.com/pornstars'), title="Pornstars", thumb=GetThumb(url='http://www.xvideos.com')))
  oc.add(DirectoryObject(key=Callback(ShowHTML, pTitle="Pornstars", url='http://www.xvideos.com/channels'), title="Channels", thumb=GetThumb(url='http://www.xvideos.com')))
 
  oc.add(InputDirectoryObject(key = Callback(Search), title = 'Search Videos', prompt = 'Search Videos'))

  return oc


#################################################################################################################
# This function is an example of parsing data from a html page
@route(PREFIX + '/showhtml')
def ShowHTML(pTitle,url):

  oc = ObjectContainer(title2=pTitle)
  if '/pornstars-click/' in url:
    url=WebsiteURL+'/profiles/'+url.split('/')[5]
 
    
  html = HTML.ElementFromURL(url)
  xvideosBest="thumb-block "
  pURL=url 
  if len(html.xpath('//div[@class="thumbBlock"]'))>0:
    xvideosBest="thumbBlock"
  if len(html.xpath('//title//text()'))>0:    
    if 'Pornstar page' in html.xpath('//title//text()')[0]:
    
        html= HTML.ElementFromURL(url+'/pornstar_videos/0/0')
        pURL=url+'/pornstar_videos/0/0'
    else:
	if 'Channel page' in html.xpath('//title//text()')[0]:
	    html=HTML.ElementFromURL(url+'/uploads/0/0')
	    pURL=url+'/uploads/0/0'
 
  for video in html.xpath('//div[@class="%s"]' %xvideosBest):
    try:
	if '/profiles/' not in pURL and '/pornstars-click' not in pURL:
	    if len(video.xpath('./div/div/a//@href'))==0:
	    
		url = video.xpath('./p/a//@href')[0]
		url = WebsiteURL + url
		title = video.xpath('./p/a//text()')[0]
	    	thumb = THUMB_REG.search(video.xpath('./div/div/script//text()')[0]).group(1)
		oc.add(VideoClipObject(
		    url = url, 
		    title = title,
		    thumb = thumb))
	    else:
	        url = video.xpath('./p/a//@href')[0]
	        url = WebsiteURL + url
	        title = video.xpath('./p/a//text()')[0]
	        oc.add(DirectoryObject(key=Callback(ShowHTML, url=url,pTitle=title), title=title, thumb = THUMB_REG.search(video.xpath('./div/div/a/script//text()')[0]).group(1)))
	else:
	    
	    url = video.xpath('./div/p/a//@href')[0]
	    
	    url = WebsiteURL + url
	    title = video.xpath('./div/p/a//text()')[0]
	    thumb = video.xpath('./div/div/a/img//@src')[0]
	    oc.add(VideoClipObject(
		url = url, 
		title = title,
		thumb = thumb))
    	    	    

    except:
	Log.Debug('nothing')
  try:
    if len(html.xpath("//div[contains(@class,'pagination')]/ul/li/a[@class='active']"))==0:
	if '/uploads/0' in pURL or '/pornstar_videos/0' in pURL:
	    splittedURL=pURL.split('/')
	    splittedURL[-1]=str(int(splittedURL[-1])+1)
	    nextURL = ('/').join(splittedURL)
	else:
	    nextURL = WebsiteURL+html.xpath("//div[contains(@class,'pagination')]//a[@class='no-page']//@href")[0]
	
    else:
	nextURL = WebsiteURL+html.xpath("//div[contains(@class,'pagination')]/ul/li/a[@class='active']/../following-sibling::li/a//@href")[0]
	
    if '&' in nextURL:
        oc.add(NextPageObject(key=Callback(ShowHTML, url=nextURL, pTitle='Page '+nextURL.split('=')[-1]), title="More ..."))
    else:
        oc.add(NextPageObject(key=Callback(ShowHTML, url=nextURL, pTitle='Page '+nextURL.split('/')[-1]), title="More ..."))

    	
  except:
    # do nothing
    
    nextURL = ""



# it will loop through and return the values for all items in the page 
  return oc



#######################################################################################################################

#############################################################################################################################
# This is a function to pull the thumb from a the head of a page
@route(PREFIX + '/getthumb')
def GetThumb(url):
  page = HTML.ElementFromURL(url)
  try:
    thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
    if not thumb.startswith('http://'):
      thumb = http + thumb
  except:
    thumb = R(ICON)
  return thumb


@route(PREFIX + '/Search')
def Search(query="test"):
    search=String.Quote(query, usePlus=True)
    return ShowHTML(url="http://xvideos.com/?k="+search, pTitle="Search xvideos")


