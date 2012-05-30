from item import *
plural = "posts"

def new(item_id, timestamp=time.time()):
  return post(item_id, timestamp)

class post(item):
  def __init__(self, new_id='', timestamp = time.time()):
    item.__init__(self, new_id, timestamp)
    self.sorted = ['title','body']
    self.title = ''
    self.body = ''
    
  def loadfromxml(self, xml):
    xml, meta, body = item.loadfromxml(self,xml)
    self.title = xml_quick_extract(meta, 'title')[0]
    self.body = body

  def getTitle(self):
    return self.title

  def render(self, mode='', extras=None):
    nice_time = time.strftime('%b %d, %Y', time.gmtime(self.timestamp))
  
    if (mode == 'short'):
      contents = self.body
      contents = strip_comments(contents)
      contents = wikiparse(contents,options['base_url'])
      chopped_contents = sentence_chop(contents, 800)
      
      read_more_text = 'read more...'
      if (chopped_contents == contents):
        read_more_text = '#'
      
      chopped_contents = close_tags(chopped_contents)
      results = '''
<div id="item_%(id)s" class="item post">
<div class="header headline">
%(headline)s
</div>
''' % {'headline':self.title,'id':self.id}

      results += '''
<div class="header date">
 posted %(nice_time)s
</div>
    
<div class="border">
<div class="text">
%(text)s
</div>
  <div class="more_link">
    <a href="%(base_url)s/view/%(id)s">%(read_more_text)s</a>
  </div>
</div>
''' % {'base_url':options['base_url'],'nice_time':nice_time,'text':chopped_contents,'id':self.id,'read_more_text':read_more_text}
      results += '</div>'
      
    else:
      contents = self.body
      contents = wikiparse(contents, options['base_url'])
      results = '''
<div id="item_%(id)s" class="item post">
<div class="header headline">
%(headline)s
</div>
''' % {'headline':self.title,'id':self.id}

      results += '''
<div class="header date">
 posted %(nice_time)s
</div>
    
<div class="border">
<div class="text">
%(text)s
</div>
</div>
''' % {'nice_time':nice_time,'text':contents}
      results += '</div>'
      
    return results

  def toweb(self):
    return merge(item.toweb(self),{
            'plural':plural,
            'title':self.title,
            'body':urllib.parse.quote(self.body)})
  
  def save(self, filename):
    item.unicodeify_all(self)
    meta = ''
    meta += '<title>'+self.title+'</title>\n'
    item.really_save(self,filename,meta,self.body)
