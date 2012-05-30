from item import *
plural = "pages"

def new(item_id, timestamp=time.time()):
  return page(item_id, timestamp)

class page(item):
  def __init__(self, new_id='', timestamp = time.time()):
    item.__init__(self, new_id, timestamp)
    self.sorted = ['headline','contents']
    
    # remove non-alphanumeric from id
    p = re.compile('\W')
    new_id = p.sub('',new_id) 
    self.id = new_id
    
    self.headline = ''
    self.contents = ''
    
    
  def loadfromxml(self, xml):
    xml, meta, body = item.loadfromxml(self,xml)
    self.headline = xml_quick_extract(meta, 'headline')[0]
    self.contents = body
    
  def render(self, mode='', extras=None):
    nice_time = time.strftime('%b %d, %Y', time.gmtime(self.timestamp))
    contents = wikiparse(self.contents)
    results = '''
<div id="page_%(id)s" class="item">
<div class="header headline">
%(headline)s
</div>
''' % {'headline':self.headline,'id':self.id}

    results += '''
<div class="header date">
 %(nice_time)s
</div>
    
<div class="border">
<div class="text">
%(contents)s
</div>
</div>
''' % {'nice_time':nice_time,'contents':contents}
    results += '</div>'      
    return results
    
  def toweb(self):
    return merge(item.toweb(self),{
            'plural':plural,
            'headline':self.headline,
            'contents':self.contents})

  def save(self, filename):
    item.unicodeify_all(self)
    filename = filename.replace('/page_','/')
    meta = ''
    meta = '<headline>'+self.headline+'</headline>\n'
    item.really_save(self,filename,meta,self.contents)
  
    
    

