import time,urllib.request,urllib.parse,urllib.error,fcntl,codecs
from config import *
from blog_my_lib import *
from re import escape, compile, sub

class item:
  def __init__(self, new_id, timestamp):
    self.id = new_id
    self.timestamp = timestamp
    self.hidden = ['id','timestamp','hidden','sorted','disable_comments','draft']
    self.sorted = []
    self.disable_comments = False
    self.draft = False

  def loadfromxml(self, xml):
    # xml = item.unicodeify_text(self,xml)
    meta = xml_quick_extract(xml, 'meta')[0]
    self.disable_comments = bool(xml_quick_extract(meta, 'disable_comments')[0])
    self.draft = bool(xml_quick_extract(meta, 'draft')[0])
    if not '</meta>' in xml: return xml, meta, ''
    start = xml.index('</meta>')
    body = xml[start+7:]
    return xml, meta, body
    
    
  def render(self, mode='', extras=None):
    return ''

  def toweb(self):
    return {'type':self.__class__.__name__,
            'id':self.id,
            'disable_comments':self.disable_comments,
            'draft':self.draft}
    
  def tofeed(self):
    return ''

  def save(self, filename):
    pass
    
  def getTitle(self):
    return ''
    
  def unicodeify_all(self):
    pass

  def unicodeify_text(self,text):
    try:
      return text.encode('utf-8', 'replace')
    except UnicodeDecodeError:
      return str(text,'utf-8', 'replace')

  def really_save(self, filename, meta='', data=''):
    ent = {chr(i):'&#' + str(i) + ';' for i in range(128,1024)}
    ent.update({chr(i):'&#' + str(i) + ';' for i in range(8000,9999)})
    ent.update({'\n\n':'\n</p>\n<p>\n','...':'&hellip;'})
    regex = compile("(%s)" % "|".join(map(escape, ent.keys())))
    item.unicodeify_all(self)
    contents = ''
    contents += '<meta>\n'
    if self.disable_comments:
      contents += '<disable_comments>'+str(int(self.disable_comments))+'</disable_comments>\n'
    if self.draft:
      contents += '<draft>'+str(int(self.draft))+'</draft>\n'
    contents += regex.sub(lambda mo: ent[mo.string[mo.start():mo.end()]], meta)
    contents += '</meta>\n'
    
    #FIXME: This logic REALLY belongs elsewhere.
    if data[0:3] != '<p>':
        data = '<p>' + data + '</p>'
    contents += regex.sub(lambda mo: ent[mo.string[mo.start():mo.end()]], data)
  
    FILE = codecs.open(filename, 'w', "utf-8")
    fcntl.flock(FILE, fcntl.LOCK_EX)
    FILE.write(contents)
    fcntl.flock(FILE, fcntl.LOCK_UN)
    FILE.close()

