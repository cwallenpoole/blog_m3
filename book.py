from item import *
plural = "books"

def new(item_id, timestamp=time.time()):
  return book(item_id, timestamp)

class book(item):
  def __init__(self, new_id='', timestamp = time.time()):
    item.__init__(self, new_id, timestamp)
    self.sorted = ['isbn','title','author','text']
    self.title = ''
    self.author = ''
    self.isbn = ''
    self.text = ''

  def loadfromxml(self, xml):
    xml, meta, body = item.loadfromxml(self,xml)
    self.disable_comments = bool(xml_quick_extract(meta, 'disable_comments')[0])
    self.title = xml_quick_extract(meta, 'title')[0]
    self.author = xml_quick_extract(meta, 'author')[0]
    self.isbn = xml_quick_extract(meta, 'isbn')[0]
    self.text = body

  def getTitle(self):
    return self.title
    
  def render(self, mode='', extras=None):
    nice_time = time.strftime('%b %d, %Y', time.gmtime(self.timestamp))
    if mode == 'short':
      contents = self.text
      contents = wikiparse(contents, options['base_url'])
      contents = sentence_chop(contents, 800)
      contents = close_tags(contents)
      results = '''
<div id="item_%(id)s" class="item book">
  <div class="header headline">
  %(headline)s
    <div class="author">
    By %(author)s
    </div>
  </div>
  <div class="header date">
    posted %(nice_time)s
  </div>
    
  <div class="border">
    <div class="text">
''' % {'nice_time':nice_time,'headline':self.title,'id':self.id,'author':self.author}
      
      if not self.isbn == '':
        results += '''
    <img class="cover" src="http://images.amazon.com/images/P/%(isbn)s.01._PB_THUMBZZZ_.jpg"/>
''' % {'isbn':self.isbn}

      results += '''
    %(text)s</div>
    <div class="more_link">
      <a href="%(base_url)s/view/%(id)s">read more...</a>
    </div>
  </div>
</div>
''' % {'base_url':options['base_url'],'nice_time':nice_time,'text':contents,'id':self.id}
    else:
      contents = self.text
      contents = wikiparse(contents, options['base_url'])
      results = '''
<div id="item_%(id)s" class="item book">
<div class="header headline">
%(headline)s
<div class="author">
By %(author)s
</div>
</div>
<div class="header date">
 posted %(nice_time)s
</div>
    
<div class="border">
    <div class="text">
''' % {'nice_time':nice_time,'headline':self.title,'id':self.id,'author':self.author}

      #if not self.isbn == '':
      results += '''
<div class="cover"><img src="http://images.amazon.com/images/P/%(isbn)s.01._PB_SCMZZZZZZZ_.jpg"/></div>
''' % {'isbn':self.isbn}

      results += '''
%(text)s</div>
</div>
''' % {'nice_time':nice_time,'text':contents,'id':self.id}

      results += '</div>'      
      
    return results


  def toweb(self):
    return merge(item.toweb(self),{
            'plural':plural,
            'title':self.title,
            'author':self.author,
            'isbn':self.isbn,
            'text':self.text})
            
  def save(self, filename):
    item.unicodeify_all(self)
    meta = ''
    meta += '<title>'+self.title+'</title>\n'
    meta += '<author>'+self.author+'</author>\n'
    if not self.isbn == '':
      meta += '<isbn>'+self.isbn+'</isbn>\n'
    item.really_save(self,filename,meta,self.text)



      
