# -*- coding: utf-8 -*-
__author__ = 'Stuart McCulloch Anderson'

import urllib
import urllib2
import argparse
import json
import hashlib
import errno
import os,sys
import ntpath
from shutil import copyfile
import subprocess

class JsonObject:
    def __init__(self):
    #    self.data = {}
        pass

    def json_able(self):
        return self.__dict__
        
    #def __setitem__(self, key, item): 
    #    self.data[key] = item

class JsonRpc(JsonObject):
    # noinspection PyShadowingBuiltins,PyMissingConstructor
    def __init__(self, id, method):
        self.jsonrpc = "2.0"
        self.id = id
        self.method = method

class JsonFilter(JsonObject):
    # noinspection PyMissingConstructor
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def removeEmptyFolders(path, removeRoot=True):
  'Function to remove empty folders'
  if not os.path.isdir(path):
    return

  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)

  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0 and removeRoot:
    print "Removing empty folder:", path
    os.rmdir(path)

def complex_handler(obj):
    if hasattr(obj, 'json_able'):
        return obj.json_able()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def api_req_post_data(path, data, debug=False):
    global api_auth_name

    if debug:
        print path

    jsonForRequest = json.dumps(data, default=complex_handler)
    reqQuery = urllib2.Request(path, data=jsonForRequest, headers={'Content-type': 'application/json'})
    reqQuery.add_header("Authorization", api_auth_name)
    reqQuery.get_method = lambda: 'POST'

    try:
        apiAccessToken
    except NameError:
        # noinspection PyUnusedLocal
        boiler = 0
    else:
        reqQuery.add_header("X-MediaBrowser-Token", apiAccessToken)

    jsonUrl = urllib2.urlopen(reqQuery).read()

    if debug:
        print jsonUrl

    if jsonUrl != "":
        jsonDataReturn = json.loads(jsonUrl)
        if hasattr(jsonDataReturn, 'get') and jsonDataReturn.get("error") is not None:
            print "Error: " + jsonDataReturn.get("error").get("message")
            print jsonForRequest

        return jsonDataReturn
    else:
        return "Ok"

def api_req_post(path, debug=False):
    global api_auth_name

    if debug:
        print path

    reqQuery = urllib2.Request(path, data="", headers={'Content-type': 'application/json'})
    reqQuery.add_header("Authorization", api_auth_name)
    reqQuery.get_method = lambda: 'POST'

    try:
        apiAccessToken
    except NameError:
        # noinspection PyUnusedLocal
        boiler = 0
    else:
        reqQuery.add_header("X-MediaBrowser-Token", apiAccessToken)

    jsonUrl = urllib2.urlopen(reqQuery).read()

    if debug:
        print jsonUrl

    if jsonUrl != "":
        jsonDataReturn = json.loads(jsonUrl)
        if hasattr(jsonDataReturn, 'get') and jsonDataReturn.get("error") is not None:
            print "Error: " + jsonDataReturn.get("error").get("message")

        return jsonDataReturn
    else:
        return "Ok"

def api_req_delete(path, debug=False):
    global api_auth_name

    if debug:
        print path

    reqQuery = urllib2.Request(path, data="", headers={'Content-type': 'application/json'})
    reqQuery.add_header("Authorization", api_auth_name)
    reqQuery.get_method = lambda: 'DELETE'

    try:
        apiAccessToken
    except NameError:
        # noinspection PyUnusedLocal
        boiler = 0
    else:
        reqQuery.add_header("X-MediaBrowser-Token", apiAccessToken)

    jsonUrl = urllib2.urlopen(reqQuery).read()

    if debug:
        print jsonUrl

    if jsonUrl != "":
        jsonDataReturn = json.loads(jsonUrl)
        if hasattr(jsonDataReturn, 'get') and jsonDataReturn.get("error") is not None:
            print "Error: " + jsonDataReturn.get("error").get("message")

        return jsonDataReturn
    else:
        return "Ok"

def api_req_get(path, debug=False):
    global api_auth_name

    if debug:
        print path

    reqQuery = urllib2.Request(path, headers={'Content-type': 'application/json'})
    reqQuery.add_header("Authorization", api_auth_name)

    try:
        apiAccessToken
    except NameError:
        # noinspection PyUnusedLocal
        boiler = 0
    else:
        reqQuery.add_header("X-MediaBrowser-Token", apiAccessToken)

    jsonUrl = urllib2.urlopen(reqQuery).read()

    if debug:
        print jsonUrl

    if jsonUrl != "":
        jsonDataReturn = json.loads(jsonUrl)
        if hasattr(jsonDataReturn, 'get') and jsonDataReturn.get("error") is not None:
            print "Error: " + jsonDataReturn.get("error").get("message")

        return jsonDataReturn
    else:
        return "Ok"

def api_req_get_download(path, filepath='/tmp/file.mp3', debug=False):
    global api_auth_name, debugprint

    filename = ntpath.basename(filepath)
    filepath = filepath.replace(filename, "")

    if os.path.isfile(filepath + filename):
        return True
    else:
        mkdir_p(filepath)

        reqQuery = urllib2.Request(path, headers={'Content-type': 'application/json'})
        reqQuery.add_header("Authorization", api_auth_name)

        try:
            apiAccessToken
        except NameError:
            # noinspection PyUnusedLocal
            boiler = 0
        else:
            reqQuery.add_header("X-MediaBrowser-Token", apiAccessToken)

        fileOnline = urllib2.urlopen(reqQuery)

        fileDownloaded = open(filepath + filename, 'wb')
        meta = fileOnline.info()
        file_size = int(meta.getheaders("Content-Length")[0])

        df = subprocess.Popen(["df", filepath], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()

        if available > (file_size / 100):
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = fileOnline.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                fileDownloaded.write(buffer)
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                if debugprint:
                    print status,

            fileDownloaded.close()

            return True
        else:
            return False

def authenticate_api():
    global apiUserId, apiAccessToken, apiSessionId, api_user, api_pass
    doc = JsonObject()
    doc.Username = api_user
    doc.password = hashlib.sha1(api_pass).hexdigest()
    jsonrt = api_req_post_data(url + "/Users/AuthenticateByName?format=json", doc)
    apiUserId = jsonrt.get("User").get("Id")
    apiSessionId = jsonrt.get("SessionInfo").get("Id")
    apiAccessToken = jsonrt.get("AccessToken")

def copy_support_file(originalFile, newPath):
    if os.path.isfile(originalFile) and not os.path.isfile(newPath + ntpath.basename(originalFile)):
        copyfile(originalFile, newPath + ntpath.basename(originalFile))

def remove_support_files(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

    if "/Movies/" in file_path:
        filename = ntpath.basename(file_path)
        fileext  = file_path.split(".")[-1]
        filepath = os.path.dirname(file_path) + "/"

        if os.path.isfile(file_path.replace("."+fileext, ".nfo")):
            os.remove(file_path.replace("."+fileext, ".nfo"))
        if os.path.isfile(filepath + "fanart.jpg"):
            os.remove(filepath + "fanart.jpg")
        if os.path.isfile(filepath + "landscape.jpg"):
            os.remove(filepath + "landscape.jpg")
        if os.path.isfile(filepath + "logo.png"):
            os.remove(filepath + "logo.png")
        if os.path.isfile(filepath + "poster.jpg"):
            os.remove(filepath + "poster.jpg")

        if os.path.isdir(filepath):
            files = os.listdir(filepath)
            if len(files) == 0:
                os.rmdir(filepath)

    elif "/TV/" in file_path or "/Documentaries/" in file_path or "/Podcasts/Videos/" in file_path:
        filename   = ntpath.basename(file_path)
        fileext    = file_path.split(".")[-1]
        filepath   = os.path.dirname(file_path) + "/"
        fileseason = file_path.split("/")[-2]
        fileshow   = file_path.split("/")[-3]

        if os.path.isfile(file_path.replace("."+fileext, ".nfo")):
            os.remove(file_path.replace("."+fileext, ".nfo"))
        if os.path.isfile(file_path.replace("."+fileext, "-thumb.jpg")):
            os.remove(file_path.replace("."+fileext, "-thumb.jpg"))

        if os.path.isdir(filepath):
            files = os.listdir(filepath)
            if len(files) == 0:
                if os.path.isfile(filepath.replace(fileseason + "/", "") + fileseason.lower().replace(" ", "") + "-poster.jpg"):
                    os.remove(filepath.replace(fileseason + "/", "") + fileseason.lower().replace(" ", "") + "-poster.jpg")

                os.rmdir(filepath)

        if os.path.isdir(filepath.replace(fileseason + "/", "")):
            anotherSeason = False
            files = os.listdir(filepath.replace(fileseason + "/", ""))
            if len(files):
                for file in files:
                    if "Season " in file and os.path.isdir(filepath.replace(fileseason + "/", "") + file):
                        anotherSeason = True

            if not anotherSeason:
                if os.path.isfile(filepath.replace(fileseason + "/", "") + "banner.jpg"):
                    os.remove(filepath.replace(fileseason + "/", "") + "banner.jpg")
                if os.path.isfile(filepath.replace(fileseason + "/", "") + "fanart.jpg"):
                    os.remove(filepath.replace(fileseason + "/", "") + "fanart.jpg")
                if os.path.isfile(filepath.replace(fileseason + "/", "") + "logo.jpg"):
                    os.remove(filepath.replace(fileseason + "/", "") + "logo.jpg")
                if os.path.isfile(filepath.replace(fileseason + "/", "") + "poster.jpg"):
                    os.remove(filepath.replace(fileseason + "/", "") + "poster.jpg")
                if os.path.isfile(filepath.replace(fileseason + "/", "") + "tvshow.nfo"):
                    os.remove(filepath.replace(fileseason + "/", "") + "tvshow.nfo")

                if os.path.isdir(filepath.replace(fileseason + "/", "")):
                    files = os.listdir(filepath.replace(fileseason + "/", ""))
                    if len(files) == 0:
                        os.rmdir(filepath.replace(fileseason + "/", ""))

    elif "/Music Videos/" in file_path or "/Music/Videos/" in file_path:
        filename   = ntpath.basename(file_path)
        fileext    = file_path.split(".")[-1]
        filepath   = os.path.dirname(file_path) + "/"
        
        if os.path.isfile(file_path.replace("."+fileext, ".nfo")):
            os.remove(file_path.replace("."+fileext, ".nfo"))
        if os.path.isfile(file_path.replace("."+fileext, "-poster.jpg")):
            os.remove(file_path.replace("."+fileext, "-poster.jpg"))
        if os.path.isfile(file_path.replace("."+fileext, "-thumb.jpg")):
            os.remove(file_path.replace("."+fileext, "-thumb.jpg"))
    
        if os.path.isdir(filepath):
            files = os.listdir(filepath)
            if len(files) == 0:
                os.rmdir(filepath)
            else:
                anotherTrack = False
                for filename in files: 
                    if "fanart.jpg" not in filename and "logo.png" not in filename and "folder.jpg" not in filename and "artist.nfo" not in filename:
                        anotherTrack = True
                
                if not anotherTrack:
                    if os.path.isfile(filepath + "fanart.jpg"):
                        os.remove(filepath + "fanart.jpg")
                    if os.path.isfile(filepath + "poster.jpg"):
                        os.remove(filepath + "poster.jpg")
                    if os.path.isfile(filepath + "folder.jpg"):
                        os.remove(filepath + "folder.jpg")
                    if os.path.isfile(filepath + "logo.png"):
                        os.remove(filepath + "logo.png")
                    if os.path.isfile(filepath + "artist.nfo"):
                        os.remove(filepath + "artist.nfo")
                if os.path.isdir(filepath):
                    files = os.listdir(filepath)
                    if len(files) == 0:
                        os.rmdir(filepath)
                else:
                    if debugprint:
                        print "Another track found"

def post_synfiles_update(strjsonLocalItemIds):
    global apiUserId, api_deviceId, debugprint, currentFiles

    if debugprint:
        print "Synchronizing with Emby..."

    jsonSyncData = '{"LocalItemIds":[' + strjsonLocalItemIds + '],"OfflineUserIds":["' + apiUserId + '"],"TargetId":"' + api_deviceId + '"}'
    jsonSyncData = json.loads(jsonSyncData)
    sync_data = api_req_post_data(url + "/emby/Sync/Data?format=json", jsonSyncData)

    if len(sync_data.get("ItemIdsToRemove")) > 0:
        if debugprint:
            print " Emby has requested " + str(len(sync_data.get("ItemIdsToRemove"))) + " file(s) be delete"

        for ItemIdsToRemove in sync_data.get("ItemIdsToRemove"):
            try:
                if debugprint:
                    print "  " + ItemIdsToRemove + " = " + ntpath.basename(currentFiles[ItemIdsToRemove])

                remove_support_files(currentFiles[ItemIdsToRemove])
                strjsonLocalItemIds = strjsonLocalItemIds.replace('"' + ItemIdsToRemove + '",', '').replace(',"' + ItemIdsToRemove + '"', '').replace('"' + ItemIdsToRemove + '"', '')
                currentFiles.pop(ItemIdsToRemove, None)
            except:
                passon = True
        
        post_synfiles_update(strjsonLocalItemIds)
    else:
       text_file = open(dataFile, "w")
       text_file.write("%s" % json.dumps(currentFiles).encode("utf-8"))
       text_file.close()

def find_tv_show(show_name, ProductionYear):
    global all_tv_shows, apiUserId

    json_tv_shows = ""
    if all_tv_shows == "":
        json_tv_shows = api_req_get(url + "/Users/" + apiUserId + "/Items?SortBy=SortName&SortOrder=Ascending&IncludeItemTypes=Series&Recursive=true&Fields=PrimaryImageAspectRatio%2CSortName&format=json")
        all_tv_shows = json_tv_shows.get("Items")

    for show in all_tv_shows:
        if ProductionYear > 0 and show['Name'].encode('utf-8').strip() == show_name.encode('utf-8').strip() and show['ProductionYear'] == ProductionYear:
            return show
        elif ProductionYear == 0 and show['Name'].encode('utf-8').strip() == show_name.encode('utf-8').strip():
            return show

    return show_name + " - Not Found"

def find_movie(show_name, ProductionYear):
    global all_movies, apiUserId

    json_tv_shows = ""
    if all_movies == "":
        json_tv_shows = api_req_get(url + "/Users/" + apiUserId + "/Items?SortBy=SortName&SortOrder=Ascending&IncludeItemTypes=Movie&Recursive=true&Fields=PrimaryImageAspectRatio%2CSortName&format=json")
        all_movies = json_tv_shows.get("Items")

    for show in all_movies:
        if ProductionYear > 0 and show['Name'].encode('utf-8').strip() == show_name.encode('utf-8').strip() and show['ProductionYear'] == ProductionYear:
            return show
        elif ProductionYear == 0 and show['Name'].encode('utf-8').strip() == show_name.encode('utf-8').strip():
            return show

    return show_name + " - Not Found"

parser = argparse.ArgumentParser(description='Query XBMC database')
parser.add_argument('--user', dest='user', help='Title of the movie')
parser.add_argument('--pass', dest='password', help='Title of the movie')
parser.add_argument('--synctype', dest='synctype', help='Title of the movie')
parser.add_argument('--debug', dest='debugprint', help='Title of the movie')

args = parser.parse_args()
api_user = args.user
api_pass = args.password
debugprint = args.debugprint
synctype = args.synctype.lower()

if not api_pass:
    api_pass = ""

if not synctype:
    synctype = "music"

if not debugprint:
    debugprint = False
else:
    debugprint = True

url = 'http://10.1.1.1:8096'
all_tv_shows = ''
all_movies = ''
all_collection = ''
api_user = 'Stuart'
api_pass = ''
api_deviceId = hashlib.sha1(url + synctype + api_user).hexdigest()[:12]

destSrc = '/media/MediaLibrary/'
destRoot = ''

if synctype == "video":
    devName = "DynPi Sync"
    destRoot = destRoot + '/volumeUSB3/usbshare/' # Kogi Portable
elif synctype == "passport":
    devName = "NxPassport Sync"
    destRoot = destRoot + '/volumeUSB1/usbshare/Emby Media/' # My Passport
elif synctype == "pny":
    devName = "USB PNY Sync"
    destRoot = destRoot + '/volumeUSB2/usbshare/' # My Passport
elif synctype == "scandisk":
    devName = "USB ScanDisk Sync"
    destRoot = destRoot + '/volume1/public/PNYSync/' # My Passport
elif synctype == "test":
    devName = "DynPi Sync Test"
    destRoot = destRoot + '/volume1/public/DynSync/'
elif synctype == "book":
    devName = "Mobile " + synctype.title() + " Sync"
    destRoot = destRoot + '/volume1/homes/nxad/Remote Sync/BitTorrent Sync/Sync Books/'
elif synctype == "comic":
    devName = "Mobile " + synctype.title() + " Sync"
    destRoot = destRoot + '/volume1/homes/nxad/Remote Sync/BitTorrent Sync/Sync Comic/'
else:
    devName = "Mobile " + synctype.title() + " Sync"
    destRoot = destRoot + '/volume1/homes/nxad/Remote Sync/BitTorrent Sync/Sync Music/'

if not os.path.isdir(destRoot):
    if debugprint:
        print "Sync failed as " + destRoot + " is missing"
else:
    if debugprint:
        print "Starting synchronizer"
        
    dataFile = destRoot + "data.json"
    jobsFile = destRoot + "jobs.json"
    # Authenticate with the API
    api_auth_name = "MediaBrowser Client=NxFIFTEEN Emby Sync, Device=" + devName + ", DeviceId=" + api_deviceId + ", Version=0.0.0.1"
    authenticate_api()

    if debugprint:
        print "Pushing client options"
        
    jsonPayload = '{"PlayableMediaTypes":["Audio","Video"],"SupportsPersistentIdentifier":true,"SupportsMediaControl":false,"SupportsOfflineAccess":true,"SupportsSync":true,"SupportsContentUploading":false,"DeviceProfile":{"MaxStreamingBitrate":176551724,"MaxStaticBitrate":100000000,"MusicStreamingTranscodingBitrate":192000,"DirectPlayProfiles":[{"Container":"mp4,m4v","Type":"Video","VideoCodec":"h264","AudioCodec":"mp3,aac"},{"Container":"mkv","Type":"Video","VideoCodec":"h264","AudioCodec":"mp3,aac"},{"Container":"mov","Type":"Video","VideoCodec":"h264","AudioCodec":"mp3,aac"},{"Container":"opus","Type":"Audio"},{"Container":"mp3","Type":"Audio"},{"Container":"aac","Type":"Audio"},{"Container":"m4a","AudioCodec":"aac","Type":"Audio"},{"Container":"webma,webm","Type":"Audio"},{"Container":"wav","Type":"Audio"},{"Container":"webm","Type":"Video"},{"Container":"m4v,3gp,ts,mpegts,mov,xvid,vob,mkv,wmv,asf,ogm,ogv,m2v,avi,mpg,mpeg,mp4,webm,wtv","Type":"Video","AudioCodec":"aac,aac_latm,mp2,mp3,ac3,wma,dca,dts,pcm,PCM_S16LE,PCM_S24LE,opus,flac"},{"Container":"aac,mp3,mpa,wav,wma,mp2,ogg,oga,webma,ape,opus,flac,m4a","Type":"Audio"}],"TranscodingProfiles":[{"Container":"opus","Type":"Audio","AudioCodec":"opus","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"opus","Type":"Audio","AudioCodec":"opus","Context":"Static","Protocol":"http","MaxAudioChannels":"2"},{"Container":"mp3","Type":"Audio","AudioCodec":"mp3","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"mp3","Type":"Audio","AudioCodec":"mp3","Context":"Static","Protocol":"http","MaxAudioChannels":"2"},{"Container":"aac","Type":"Audio","AudioCodec":"aac","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"aac","Type":"Audio","AudioCodec":"aac","Context":"Static","Protocol":"http","MaxAudioChannels":"2"},{"Container":"wav","Type":"Audio","AudioCodec":"wav","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"wav","Type":"Audio","AudioCodec":"wav","Context":"Static","Protocol":"http","MaxAudioChannels":"2"},{"Container":"mkv","Type":"Video","AudioCodec":"mp3,aac,ac3","VideoCodec":"h264","Context":"Streaming","MaxAudioChannels":"2","CopyTimestamps":false},{"Container":"ts","Type":"Video","AudioCodec":"aac,mp3,ac3","VideoCodec":"h264","Context":"Streaming","Protocol":"hls","MaxAudioChannels":"2","EnableSplittingOnNonKeyFrames":false},{"Container":"webm","Type":"Video","AudioCodec":"vorbis","VideoCodec":"vpx","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"mp4","Type":"Video","AudioCodec":"mp3,aac,ac3","VideoCodec":"h264","Context":"Streaming","Protocol":"http","MaxAudioChannels":"2"},{"Container":"mp4","Type":"Video","AudioCodec":"mp3,aac,ac3","VideoCodec":"h264","Context":"Static","Protocol":"http"}],"ContainerProfiles":[],"CodecProfiles":[{"Type":"Video","Container":"avi","Conditions":[{"Condition":"NotEqual","Property":"CodecTag","Value":"xvid"}]},{"Type":"Video","Codec":"h264","Conditions":[{"Condition":"EqualsAny","Property":"VideoProfile","Value":"high|main|baseline|constrained baseline"},{"Condition":"LessThanEqual","Property":"VideoLevel","Value":"41"}]},{"Type":"Audio","Conditions":[{"Condition":"LessThanEqual","Property":"AudioChannels","Value":"2"}]}],"SubtitleProfiles":[{"Format":"srt","Method":"External"},{"Format":"ssa","Method":"External"},{"Format":"ass","Method":"External"},{"Format":"srt","Method":"Embed"},{"Format":"subrip","Method":"Embed"},{"Format":"ass","Method":"Embed"},{"Format":"ssa","Method":"Embed"},{"Format":"dvb_teletext","Method":"Embed"},{"Format":"dvb_subtitle","Method":"Embed"},{"Format":"dvbsub","Method":"Embed"},{"Format":"pgs","Method":"Embed"},{"Format":"pgssub","Method":"Embed"},{"Format":"dvdsub","Method":"Embed"},{"Format":"vtt","Method":"Embed"},{"Format":"sub","Method":"Embed"},{"Format":"idx","Method":"Embed"},{"Format":"smi","Method":"Embed"}],"ResponseProfiles":[{"Type":"Video","Container":"m4v","MimeType":"video/mp4"},{"Type":"Video","Container":"mov","MimeType":"video/webm"}],"MaxStaticMusicBitrate":null}}'
    api_req_post_data(url + "/emby/Sessions/Capabilities/Full", json.loads(jsonPayload))

    if debugprint:
        print "Reading from local cache"
        
    expectedFiles = []
    strjsonLocalItemIds = ""
    currentFiles = json.loads("{}")
    if os.path.isfile(dataFile):
        with open(dataFile) as data_file:
            currentFiles = json.load(data_file)

        for key in currentFiles:
            expectedFiles.append(hashlib.sha1(currentFiles[key].encode('utf-8')).hexdigest())

            if strjsonLocalItemIds == "":
                strjsonLocalItemIds = strjsonLocalItemIds + '"' + key + '"'
            else:
                strjsonLocalItemIds = strjsonLocalItemIds + ',"' + key + '"'
    
    post_synfiles_update(strjsonLocalItemIds)

    if debugprint:
        print "Updating sync jobs"

    syncJobs = json.loads("{}")
    if os.path.isfile(jobsFile):
        with open(jobsFile) as data_file:
            syncJobs = json.load(data_file)

    missingJob = False
    expectedJobs = []
    jsonSyncJobs = {}
    for key in syncJobs:
        if 'Id' in syncJobs.get(key):
            expectedJobs.append(syncJobs.get(key).get("Id"))
            jsonItemId = syncJobs.get(key).get("Id")
        else:
            if syncJobs.get(key).get("Type") == "Show":
                # Download/Search for the TV show
                if 'Year' not in syncJobs.get(key):
                    SearchProductionYear = 0
                else:
                    SearchProductionYear = syncJobs.get(key).get("Year")            
                
                target_tvshow = find_tv_show(syncJobs.get(key).get("Name"), SearchProductionYear)
                if isinstance(target_tvshow, basestring):
                    # Check TV show was found, if not a string error message is returned
                    print target_tvshow
                    missingJob = True
                else:
                    #print target_tvshow.get("Id").encode('utf-8') + " -> " + syncJobs.get(key).get("Name").encode('utf-8')
                    expectedJobs.append(target_tvshow.get("Id"))
                    jsonItemId = target_tvshow.get("Id")
            elif syncJobs.get(key).get("Type") == "Movie":
                # Download/Search for the TV show
                if 'Year' not in syncJobs.get(key):
                    SearchProductionYear = 0
                else:
                    SearchProductionYear = syncJobs.get(key).get("Year")            
                
                target_tvshow = find_movie(syncJobs.get(key).get("Name"), SearchProductionYear)
                if isinstance(target_tvshow, basestring):
                    # Check TV show was found, if not a string error message is returned
                    print target_tvshow
                    missingJob = True
                else:
                    #print target_tvshow.get("Id").encode('utf-8') + " -> " + syncJobs.get(key).get("Name").encode('utf-8')
                    expectedJobs.append(target_tvshow.get("Id"))
                    jsonItemId = target_tvshow.get("Id")
                
        if not missingJob:
            if 'Bitrate' not in syncJobs.get(key):
                Bitrate = ""
            else:
                Bitrate = syncJobs.get(key).get("Bitrate")
                
            if 'Quality' not in syncJobs.get(key):
                Quality = ""
            else:
                Quality = syncJobs.get(key).get("Quality")
                
            if 'Profile' not in syncJobs.get(key):
                Profile = ""
            else:
                Profile = syncJobs.get(key).get("Profile")
                
            if 'ItemLimit' in syncJobs.get(key):
                ItemLimit = ', "ItemLimit":"' + str(syncJobs.get(key).get("ItemLimit")) + '"'
            else:
                ItemLimit = ''
                
            if 'SyncNewContent' not in syncJobs.get(key):
                SyncNewContent = True
            else:
                if syncJobs.get(key).get("SyncNewContent") == "False":
                    SyncNewContent = False
                else:
                    SyncNewContent = True
                
            if 'UnwatchedOnly' not in syncJobs.get(key):
                UnwatchedOnly = True
            else:
                if syncJobs.get(key).get("UnwatchedOnly") == "False":
                    UnwatchedOnly = False
                else:
                    UnwatchedOnly = True
        
            jsonItemPayload = '{"userId":"' + apiUserId + '","TargetId":"' + api_deviceId + '","Bitrate":"' + str(Bitrate) + '","Quality":"' + str(Quality) + '","Profile":"' + str(Profile) + '"' + ItemLimit + ',"SyncNewContent":"' + str(SyncNewContent) + '","UnwatchedOnly":"' + str(UnwatchedOnly) + '","ItemIds":"' + jsonItemId + '"}'
            
            jsonSyncJobs[jsonItemId] = jsonItemPayload

    if missingJob:
        exit()
    
    syncJobsRules = api_req_get(url + "/emby/Sync/Jobs?TargetId=" + api_deviceId + "&format=json")
    totalJobsNo = len(syncJobsRules.get("Items"))
    if totalJobsNo == 0:
        if debugprint:
            print "Creating TV Jobs..."
            
        for missingJob in expectedJobs:
            jsonSyncData = json.loads(jsonSyncJobs[missingJob])
            sync_data = api_req_post_data(url + "/emby/Sync/Jobs?format=json", jsonSyncData)

    else:
        missingJobs = expectedJobs
    
        for syncJobRule in syncJobsRules.get("Items"):
            if syncJobRule.get("PrimaryImageItemId") in missingJobs:
                missingJobs.remove(syncJobRule.get("PrimaryImageItemId"));
            
        for missingJob in missingJobs:
            print "We're still missing " + missingJob
            jsonSyncData = json.loads(jsonSyncJobs[missingJob])
            print jsonSyncData
            sync_data = api_req_post_data(url + "/emby/Sync/Jobs?format=json", jsonSyncData)

    if debugprint:
        print "Getting sync jobs"
        
    syncJobs = api_req_get(url + "/emby/Sync/Items/Ready?TargetId=" + api_deviceId + "&format=json")
    
    precentJobNo = 0
    currentJobNo = 0
    totalJobNo = len(syncJobs)
    
    if totalJobNo > 0:
        if debugprint:
            print str(len(syncJobs)) + " jobs ready for sync"

        for syncJob in syncJobs:
            currentJobNo = currentJobNo + 1
            precentJobNo = "[%3.2f%%]" % (currentJobNo * 100. / totalJobNo)
            
            originalFilePath = syncJob.get("Item").get("MediaSources")[0].get("Path")
            originalFileId   = syncJob.get("Item").get("MediaSources")[0].get("Id")

            if debugprint:
                print " " + precentJobNo + "% " + str(currentJobNo) + " / " + str(totalJobNo) + " | " + syncJob.get("SyncJobName") + " - " + syncJob.get("Item").get("Name")
                print "  From: " + originalFilePath

            filePathName = destRoot + originalFilePath
            filePathName = filePathName.replace(destSrc, "")

            if synctype == "music":
                filePathName = filePathName.replace('Music/Albums/', 'Albums/')
                filePathName = filePathName.replace('Music/Videos/', 'Music Videos/')

            if debugprint:
                print "  To  : " + filePathName
                
            originalFilePath = originalFilePath.replace("/media/MediaLibrary/", "/volume2/MediaFiles/")
            if debugprint:
                print "  Rewritten to  : " + originalFilePath

            if api_req_get_download(url + "/emby/Sync/JobItems/" + syncJob.get("SyncJobItemId") + "/File", filePathName):
                api_req_post(url + "/emby/Sync/JobItems/" + syncJob.get("SyncJobItemId") + "/Transferred")
                
                expectedFiles.append(hashlib.sha1(filePathName.encode('utf-8')).hexdigest())
                currentFiles[originalFileId] = filePathName

                if strjsonLocalItemIds == "":
                    strjsonLocalItemIds = strjsonLocalItemIds + '"' + originalFileId + '"'
                else:
                    strjsonLocalItemIds = strjsonLocalItemIds + ',"' + originalFileId + '"'

                if "/Movies/" in originalFilePath:
                    destpath = os.path.dirname(filePathName) + "/"

                    filename = ntpath.basename(originalFilePath)
                    fileext  = originalFilePath.split(".")[-1]
                    filepath = os.path.dirname(originalFilePath) + "/"

                    copy_support_file(originalFilePath.replace("."+fileext, ".nfo"), destpath)
                    copy_support_file(filepath + "fanart.jpg", destpath)
                    copy_support_file(filepath + "landscape.jpg", destpath)
                    copy_support_file(filepath + "logo.png", destpath)
                    copy_support_file(filepath + "poster.jpg", destpath)

                elif "/TV/" in originalFilePath or "/Documentaries/" in originalFilePath or "/Podcasts/Videos/" in originalFilePath or "/YouTube TV/" in originalFilePath or "/Workout/" in originalFilePath:
                    destpath = os.path.dirname(filePathName) + "/"

                    filename   = ntpath.basename(originalFilePath)
                    fileext    = originalFilePath.split(".")[-1]
                    filepath   = os.path.dirname(originalFilePath) + "/"
                    fileseason = filepath.split("/")[-2]
                    fileshow   = filepath.split("/")[-3]

                    copy_support_file(originalFilePath.replace("."+fileext, ".nfo"), destpath)
                    copy_support_file(originalFilePath.replace("."+fileext, "-thumb.jpg"), destpath)
                    copy_support_file(filepath + "../banner.jpg", destpath + "../")
                    copy_support_file(filepath + "../fanart.jpg", destpath + "../")
                    copy_support_file(filepath + "../logo.jpg", destpath + "../")
                    copy_support_file(filepath + "../poster.jpg", destpath + "../")
                    copy_support_file(filepath + "../tvshow.nfo", destpath + "../")
                    copy_support_file(filepath + "../" + fileseason.lower().replace(" ", "") + "-poster.jpg", destpath + "../")

                elif "/Music/Albums/" in originalFilePath:
                    if debugprint and not True:
                        print "No Support files for music albums"

                elif "/Music/Videos/" in originalFilePath:
                    destpath = os.path.dirname(filePathName) + "/"
                    
                    fileext    = originalFilePath.split(".")[-1]
                    filepath   = os.path.dirname(originalFilePath) + "/"

                    copy_support_file(originalFilePath.replace("."+fileext, ".nfo"), destpath)
                    copy_support_file(originalFilePath.replace("."+fileext, "-poster.jpg"), destpath)
                    copy_support_file(originalFilePath.replace("."+fileext, "-thumb.jpg"), destpath)
                    
                    copy_support_file(filepath + "fanart.jpg", destpath)
                    copy_support_file(filepath + "logo.png", destpath)
                    copy_support_file(filepath + "folder.jpg", destpath)
                    copy_support_file(filepath + "artist.nfo", destpath)

                else:
                    if debugprint:
                        print "Unknown file type " + originalFilePath

                text_file = open(dataFile, "w")
                text_file.write("%s" % json.dumps(currentFiles).encode("utf-8"))
                text_file.close()

    else:   
        if debugprint:
            print "No jobs ready for sync"

    if debugprint:
        print "Checking for orphaned files in " + destRoot
        
    for root, directories, filenames in os.walk(destRoot):
        for filename in filenames:
            if ".stfolder" not in filename and "data.json" not in filename and "jobs.json" not in filename and ".quarantine" not in filename and "landscape.jpg" not in filename and "logo.png" not in filename and "-thumb.jpg" not in filename and ".nfo" not in filename and "poster.jpg" not in filename and "banner.jpg" not in filename and "fanart.jpg" not in filename and "tvshow.nfo" not in filename:

                filehash = os.path.join(root,filename)
                filehash = hashlib.sha1(filehash).hexdigest()
    
                if filehash not in expectedFiles:
                    if debugprint:
                        print " Removing " + filename
    
                    remove_support_files(os.path.join(root,filename))

if debugprint:
    print "Sync " + synctype + " completed"

