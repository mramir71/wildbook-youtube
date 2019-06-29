# Requires Google api client library
# pip install --upgrade google-api-python-client

from googleapiclient.discovery import build

class YouTube:
    def __init__(self, KEY, db=None):
        self._YOUTUBE_API_SERVICE_NAME = 'youtube'
        self._YOUTUBE_API_VERSION = 'v3'
        self._KEY = KEY
        self.youtube = build(self._YOUTUBE_API_SERVICE_NAME, self._YOUTUBE_API_VERSION, 
                             developerKey=self._KEY)
        
        self.lastSearch = None
        self.results = []
        
        self.db = db
    
    # Uses youtube.search() API method
    def search(self, q, limit=1, fields=False, details=False, links=False, videoOnly=False, save=False):
        ''' 
        q - search query, (ex. "Whale Shark")
        limit - number of results (ex. 10 or 100)
        fields - Retrieve only selected fields (ex. True, False)
        details - Retrieves more detailed information about the video (ex. True, False)
                  Cannot be True when videoOnly=False.
        links - Generate YouTube video links for each search result. 
                Can be found in video['url'] (ex. True, False) 
        videosOnly - Return only videos from the result (ex. True, False)
        save - Saves all retrieved videos to database (ex. True, False)
        '''
        if (details and not videoOnly):
            print('You cannot use details=True and videoOnly=False together. But any other combination is valid.')
            return
        
        if (save):
            if (not self.db):
                save = False
                print("Please provide 'db' argument with an instance to database to save video(s).")
        
        # Quering the result
        searchResult = self.youtube.search().list(
            q=q,
            part='snippet',
            fields='items(id,snippet(publishedAt,channelId,title,description))' if fields else '*',
            type='video' if videoOnly else 'video,channel,playlist',
            maxResults=limit
        ).execute()
        self.lastSearch = searchResult['items']
                
        
        # Handling additional parameters
        if (details or save or links):
            for item in self.lastSearch:
                
                # Quering more details for this result
                if (details):
                    details = self.videos(item['id']['videoId'], fields=True)
                    for prop in details[0]:
                        try:
                            item[prop].update(details[0][prop])
                        except KeyError:
                            item[prop] = details[0][prop]
                            
                # Generating YouTube video links
                if (links):
                    if (item['id']['kind'] == 'youtube#video'):
                        item['url'] = 'https://youtu.be/' + item['id']['videoId']
                    elif (item['id']['kind'] == 'youtube#channel'):
                        item['url'] = 'https://www.youtube.com/channel/' + item['id']['channelId']

                # Saving item in database
                if (save):
                    self.db.addVideo(item['id']['videoId'], item)
                    

        # Appeding result to all previous search results
        self.results = self.lastSearch + self.results
        return self.lastSearch
    
    # Retrueve info about specific video(s)
    def videos(self, id, fields=False):
        searchResult = self.youtube.videos().list(
            part='snippet,statistics',
            fields='items(snippet(tags),statistics)' if fields else '*',
            id=id
        ).execute()
        
        return searchResult['items']
    
    # Retrieve info about channel
    def channel(self, id, fields=False):
        searchResult = self.youtube.channels().list(
            part='contentDetails,snippet',
            fields='' if fields else '*',
            id=id
        ).execute()
        
        return searchResult