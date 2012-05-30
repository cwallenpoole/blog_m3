import simplejson,time,fcntl
from blog_my_lib import *
  
class comment:
  def __init__(self, item_id='', timestamp = time.time()):
    self.hidden = ['id','timestamp','hidden','sorted']
    self.sorted = ['text','attr']
    self.id = None
    self.hashcode = GenRandomString(16)
    self.item_id = item_id
    self.timestamp = timestamp
    self.text = ''
    self.link = ''
    self.by = ''

  def loadfromxml(self, xml):
    self.text = xml_quick_extract(xml, 'text')[0]
    self.hashcode = xml_quick_extract(xml, 'hashcode')[0]
    self.by = xml_quick_extract(xml, 'by')[0]
    self.link = xml_quick_extract(xml, 'link')[0]
    self.id = xml_quick_extract(xml, 'id')[0]
    self.timestamp = xml_quick_extract(xml, 'timestamp')[0]
    
  def loadfromjson(self, jsontext):
    #if type(jsontext) is unicode:
    #  jsontext = jsontext.encode('utf-8') 
  
  
    jsondata = simplejson.loads(jsontext)
    self.text = jsondata['text']
    self.hashcode = jsondata['hashcode']
    self.by = jsondata['by']
    self.link = jsondata['link']
    self.id = jsondata['id']
    self.timestamp = jsondata['timestamp']
    
    
  def render(self, extras=None):
    t = self.timestamp
    nice_time = time.strftime('%b %d, %Y', time.gmtime(int(t)))
    
    contents = self.text 
    contents = wikiparse(contents)
    
    byline = self.by
    if not self.link == '':
      byline = '<a href="http://'+self.link+'">'+self.by+'</a>'
      if self.link.find('@') > 0:
        byline = '<a href="mailto:'+self.link+'">'+self.by+'</a>'
      
    
    results = '''
<div id="item_%(item_id)s_comment_%(id)s" class="comment">
<div class="header headline">
Comment by %(by)s
</div>

<div class="header date">
 posted %(nice_time)s
</div>

<div class="border">
<div class="text">
%(text)s
</div>
</div>

</div>      
      
''' % {'item_id':self.item_id,'by':byline,'id':self.id,'nice_time':nice_time,'text':contents}
    return results
    
  def toweb(self):
    return {'id':self.id,
            'item_id':self.item_id,
            'by':self.by,
            'link':self.link,
            'text':self.text,
            'timestamp':self.timestamp}
            
            
  def todata(self):
    return {'id':self.id,
            'item_id':self.item_id,
            'by':self.by,
            'link':self.link,
            'text':self.text,
            'hashcode':self.hashcode,
            'timestamp':self.timestamp}
    
  
  def toxml(self):
    results += '<id>'+str(self.id)+'</id>\n'
    results += '<by>'+urllib.parse.quote_plus(self.by)+'</by>\n'
    results += '<link>'+urllib.parse.quote_plus(self.link)+'</link>\n'
    results += '<text>\n'+urllib.parse.quote_plus(self.text)+'\n</text>'
    return '<comment>\n'+results+'\n</comment>\n'
  
def commentsfromxml(xml, item_id):
  comments = []
  comment_xmls = xml_quick_extract(xml, 'comment')
  for comment_xml in comment_xmls:
    c = comment(item_id)
    c.loadfromxml(comment_xml)
    comments.append(c)
  return comments
  
def load(filename, item_id):
  FILE = open(filename, 'r')
  lines = FILE.readlines()
  FILE.close()
  file_comments = []
  for line in lines:
    c = comment(item_id)
    c.loadfromjson(line)
    file_comments.append(c)
  return file_comments
  
def get_max_id(comments):
  max = 0
  for c in comments:
    if int(c.id) > max:
      max = int(c.id)
  return max

def save(comments, filename):
  #j = json.JsonWriter()
  FILE = open(filename, 'w')
  fcntl.flock(FILE, fcntl.LOCK_EX)
  
  comment_text = ''
  for comment in comments:
    #comment_text += j.write(comment.todata())+'\n'
    comment_text += simplejson.dumps(comment.todata())+'\n'
  
  FILE.write(comment_text)
  fcntl.flock(FILE, fcntl.LOCK_UN)
  FILE.close()


     
      
