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
    def search(self, q, limit=1, fields=False, save=False):
        ''' 
        q - search query, (ex. "Whale Shark")
        limit - number of results (ex. 10 or 100)
        fields - Retrieve only selected fields (ex. True, False)
        save - Saves all retrieved videos to database (ex. True, False)
        '''
        if (save and not self.db):
            save = False
            print("Please provide 'db' argument with an instance to database to save video(s).")
        
        # Quering the result
        searchResult = self.youtube.search().list(
            q=q,
            part='snippet',
            fields='items(id,snippet(publishedAt,channelId,title,description))' if fields else '*',
            type='video',
            maxResults=limit
        ).execute()

        # Saving original YouTube responce for last search
        self.lastSearch = searchResult['items']
                
        modifiedResult = []

        # Going through each result
        for item in self.lastSearch:

            # Quering more details for this result
            details = self.videos(item['id']['videoId'], fields=True)
            for prop in details[0]:
                try:
                    item[prop].update(details[0][prop])
                except KeyError:
                    item[prop] = details[0][prop]

            # WILDBOOK FORMAT
            newItem = {
                "videoID": item['id']['videoId'],
                "title": {
                    "original": item['snippet']['title'],
                    "eng": item['snippet']['title'], #[Microsoft translate]
                },
                "tags": {
                    "original": item['snippet']['tags'],
                    "eng": item['snippet']['tags'], #[Microsoft translate]
                },
                "description": {
                    "original": item['snippet']['description'],
                    "eng": item['snippet']['description'], #[Microsoft translate]
                },
                "OCR": {
                    "original": [], #[Azure]
                    "eng": [], #[Azure, Microsoft translate]
                },
                "url": 'https://youtu.be/' + item['id']['videoId'],
                "animalsID": [], #[Wildbook]
                "curationStatus": None, #[Wildbook]
                "curationDecision": None, #[Wildbook]
                "publishedAt": item['snippet']['publishedAt'],
                "uploadedAt": None, #[YouTube]
                "duration": None, #[YouTube]
                "regionRestriction": None, #[YouTube]
                "viewCount": item['statistics']['viewCount'],
                "likeCount": item['statistics']['likeCount'],
                "dislikeCount": item['statistics']['dislikeCount'],
                "recordingDetails": {
                    "location": None, #[YouTube]
                    "date": None, #[YouTube]
                },
                "encounter": {
                    "locationIDs": [], #[Wildbook]
                    "dates": [], #[Wildbook]
                },
                "fileDetails": None, #[YouTube]
            }

            # Saving item in database
            if (save):
                self.db.addVideo(item['id']['videoId'], newItem)

            modifiedResult.append(newItem)

        # Appeding result to all previous search results
        self.results = modifiedResult + self.results
                    
        return modifiedResult
    
    # Retrueve info about specific video(s)
    def videos(self, id, fields=False):
        searchResult = self.youtube.videos().list(
            part='snippet,statistics',
            fields='items(snippet(description,tags),statistics)' if fields else '*',
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