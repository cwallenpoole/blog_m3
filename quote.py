from item import *

plural = "quotes"

def new(item_id, timestamp=time.time()):
  return quote(item_id, timestamp)

class quote(item):
  def __init__(self, new_id='', timestamp = time.time()):
    item.__init__(self, new_id, timestamp)
    self.sorted = ['text','attr']
    self.text = ''
    self.attr = ''

  def loadfromxml(self, xml):
    xml, meta, body = item.loadfromxml(self,xml)
    meta = xml_quick_extract(xml, 'meta')[0]
    self.disable_comments = bool(xml_quick_extract(meta, 'disable_comments')[0])
    self.text = xml_quick_extract(meta, 'text')[0]
    self.attr = xml_quick_extract(meta, 'attr')[0]

  def getTitle(self):
    return 'quote'
    
  def render(self, mode='', extras=None):
    nice_time = time.strftime('%b %d, %Y', time.gmtime(self.timestamp))
    
    headline = ''
    if extras and 'headline' in extras:
      headline = extras['headline']
    
    contents = self.text 
    contents = wikiparse(contents)
    
    results = '''
<div id="item_%(id)s" class="item quote">
''' % {'id':self.id}

    if not headline == '':
      results += '''
<div class="header headline">
%(headline)s
</div>
''' % {'headline':headline}

    results += '''
<div class="header date">
 posted %(nice_time)s
</div>
    
<div class="border">
<div class="text">
%(text)s
</div>
''' % {'nice_time':nice_time,'text':contents}

    if not (self.attr == None or self.attr == ''):  # if there's an author, display it
      results += '''
<div class="attr" style="text-align:right;">
%(attr)s
</div>
''' % {'attr':self.attr}

    if mode == 'short':
      results += '''
<div class="more_link">
  <a href="%(base_url)s/view/%(id)s">#</a>
</div>
''' % {'id':self.id,'base_url':options['base_url']}

    results += '</div></div>'
    return results
    
  def toweb(self):
    return merge(item.toweb(self),{
            'plural':plural,
            'text':self.text,
            'attr':self.attr})
    
  def save(self, filename):
    item.unicodeify_all(self)
    meta = ''
    meta += '<text>'+self.text+'</text>\n'
    if not self.attr == '':
      meta += '<attr>'+self.attr+'</attr>\n'
    item.really_save(self,filename,meta)

