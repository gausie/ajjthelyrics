#! /usr/bin/env/python

# License below inherited from parent project TMBOTG - Sam Gaus
#
# Copyright (c) 2013 Brett g Porter
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from bs4 import BeautifulSoup
from urlparse import urljoin
from urllib import unquote
from os.path import join
import requests

kBaseUrl = "http://lyrics.wikia.com/Andrew_Jackson_Jihad"

kOutputDir = "data"


def Log(s):
   print s

def Scrub(s):
   ''' Do whatever cleanup we need to do to turn a string (possibly with spaces
      in it) to a space-less name more usable as a file name
   '''
   kIllegalChars = "!@#$%^&*()/\\{}[];:,?~`|"
   s = s.strip()
   s = s.translate(None, kIllegalChars)
   return s.replace(" ", '-')


def MakeFilename(album, track):
   ''' given an album/filename combo, return a filename that combines them'''
   return Scrub("{0}_{1}.lyric".format(album, track))

def GetSoup(urlFragment):
   ''' - join this fragment with the base url
       - retrieve the contents at the full url
       -  Parse with BeautifulSoup & return the resulting tree of objects.
   '''

   data = requests.get(urljoin(kBaseUrl, urlFragment))
   soup = BeautifulSoup(data.text)
   return soup


def ProcessDiscography(url):
   ''' load the page at 'url' and process everything in the table of albums
      (with the id 'discog'), and in turn process each album.
   '''
   soup = GetSoup(url)
   for album in soup.find_all("ol"):
      if len(album.contents) == 0:
         continue
      albumName = album.find_previous_sibling("h2").find("span", {"class":"mw-headline"}).get_text()
      for list_item in album.contents:
         song = list_item.find("a")
         name = song.text
         urlFragment = song['href']

         ''' If the page does not exist, Wikia will give the link a "new" class. '''
         if not song.has_key("class") or "new" not in song["class"]:
            Log("Handling song '{0}'".format(name))
            ProcessTrack(albumName, name, urlFragment)
         else:
            Log("Skipping '{0}' because lyrics do not exist".format(name))


def ProcessTrack(albumName, trackName, url):
   '''
      url points at a lyrics page. The lyrics are inside a <div> that has the
      class 'lyricbox'.
   '''
   soup = GetSoup(url)
   lyrics = soup.find(attrs={"class": "lyricbox"})

   for script in lyrics(["script", "style"]):
      script.extract()

   for br in lyrics("br"):
      br.replace_with("\n")

   fileName = join(kOutputDir, MakeFilename(albumName, trackName))

   Log("  {}".format(fileName))

   with open(fileName, "wt") as f:
      f.write(lyrics.get_text().encode("UTF-8"))

if __name__ == "__main__":
   ProcessDiscography("")
