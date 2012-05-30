#!/usr/local/bin/python3 -O
from config import *
from blog_my_lib import *
import sys,urllib.request,urllib.parse,urllib.error,os,stat,re,time,datetime,math,random,fcntl,codecs,shutil  # python modules
import session,item,comments,page                        # blog_my modules                  
import web, web.template, simplejson                     # 3rd-party modules

urls = (
    '/login/(.*)', 'do_login',
    '/logout/(.*)', 'do_logout',
    '/js/get_item/(.*)/comment/(.*)', 'get_comment',
    '/js/get_item/(.*)', 'get_item',
    '/js/get_files/', 'get_files',
    '/upload_file/(.+)/(.*)', 'upload_file',
    '/delete_file', 'delete_file',
    '/move_files/', 'move_files',
    '/view/(.*)', 'view',
    '/preview/', 'preview',
    '/add_item/','add_item',
    '/update_item/','update_item',
    '/delete_item/','delete_item',
    '/delete_autosave_item/','delete_autosave_item',
    '/add_comment/','add_comment',
    '/update_comment/','update_comment',
    '/delete_comment/','delete_comment',
    '/(.+)', 'view_page',
    '/?()', 'default'
)

item_types.append('page')
item_types_plural = {}
item_types_plural_inverse = {}
item_modules = {}

# load template file
FILE = open('blog_my.html', 'r')
template_contents = FILE.read()
FILE.close()

def log(text=''):
  filename = 'log.txt'
  FILE = codecs.open(filename, 'a', "utf-8")
  fcntl.flock(FILE, fcntl.LOCK_EX)
  FILE.write(str(text)+'\n')
  fcntl.flock(FILE, fcntl.LOCK_UN)
  FILE.close()
  
 
def setup():
  if not os.path.isdir('files'):
    os.mkdir('files')
  for item_type in item_types:
    item_modules[item_type] = __import__(item_type)
    item_types_plural[item_type] = item_modules[item_type].plural
    item_types_plural_inverse[item_modules[item_type].plural] = item_type
    if not os.path.isdir(item_types_plural[item_type]):         # does directory exist?
      os.mkdir(item_types_plural[item_type])
      
def get_max_id():
  max_id = 0
  for item_type in item_types:
    if item_type == 'page': continue
    item_type_plural = item_types_plural[item_type]
    filenames = os.listdir(item_type_plural)
    for filename in filenames:
      if filename.find('_comments.') > 0: continue  # skip comments
      if filename.find('_autosave.') > 0: continue  # skip autosaved files
      file_id = int(filename[filename.rfind('_')+1:filename.rfind('.')])
      if file_id > max_id:
        max_id = file_id
  return max_id
  
def load_item_by_id(item_id):
  for item_type in item_types:
    item_type_plural = item_types_plural[item_type]
    if item_type == 'page':
      filename = item_type_plural+'/'+item_id+'.xml'
    else:
      filename = item_type_plural+'/'+item_type+'_'+item_id+'.xml'
    if os.path.isfile(filename):
      FILE = open(filename, 'r')
      contents = FILE.readlines()
      FILE.close()
      contents = ''.join(contents)
      item = item_modules[item_type].new(item_id,os.path.getmtime(filename))
      item.loadfromxml(contents)
      return (item, item_type)
  return (None,None)
  
  
def load_autosave_item(item_type, item_id):
  item_type_plural = item_types_plural[item_type]
  
  filename = item_type+'_'+item_id+'_autosave.xml'
  if item_type == 'page':
    filename = item_id+'_autosave.xml'
  
  filepath = item_type_plural+'/'+filename
  if os.path.isfile(filepath):
    FILE = open(filepath, 'r')
    contents = FILE.readlines()
    FILE.close()
    contents = ''.join(contents)
    item = item_modules[item_type].new(item_id,os.path.getmtime(filepath))
    item.loadfromxml(contents)
    return item
  return None

  
def load_comments(item_id, item_type=None):
  item_comments = []
  if item_type:
    item_type_plural = item_types_plural[item_type]
    if item_type == 'page':
      filename = item_type_plural+'/'+item_id+'_comments.json'
    else:
      filename = item_type_plural+'/'+item_type+'_'+item_id+'_comments.json'
    if os.path.isfile(filename):
      item_comments = comments.load(filename, item_id)
  else:
    for item_type in item_types:
      item_type_plural = item_types_plural[item_type]
      
      if item_type == 'page':
        filename = item_type_plural+'/'+item_id+'_comments.json'
      else:
        filename = item_type_plural+'/'+item_type+'_'+item_id+'_comments.json'

      if os.path.isfile(filename):
        item_comments = comments.load(filename, item_id)
        break
  return item_comments
  
def save_comments(item_id, item_type, cs):
  item_type_plural = item_types_plural[item_type]
  
  if item_type == 'page':
    filename = item_type_plural+'/'+item_id+'_comments.json'
  else:
    filename = item_type_plural+'/'+item_type+'_'+item_id+'_comments.json'

  comments.save(cs,filename)

def load_page(page_title):
  filename = 'pages/'+page_title+'.xml'
  if os.path.isfile(filename):
    FILE = open(filename, 'r')
    contents = FILE.read()
    FILE.close()
    p = page.page(page_title,os.path.getmtime(filename))
    p.loadfromxml(contents)
    return p
  return None

  
def load_item(item_type, filename):
  item_id = ''
  if item_type == 'page':
    item_id = filename.rstrip('.xml')
  else:
    p = re.compile('[\W^_]')
    #(item_type_plural, item_type, item_id) = p.split(filename)[0:3]
    item_id = p.split(filename)[1]
  
  filename = item_types_plural[item_type]+'/'+filename
  
  if os.path.isfile(filename):
    FILE = open(filename, 'r')
    contents = FILE.readlines()
    FILE.close()
    contents = ''.join(contents)
    item = item_modules[item_type].new(item_id,os.path.getmtime(filename))
    item.loadfromxml(contents)
    return item
  return None
  


def load_latest_item_of_each_type(backstep=0):
  latest_items = []
  for item_type in item_types:
    if item_type == 'page': continue
    latest_timestamp = 0
    latest_file = None
    item_type_plural = item_types_plural[item_type]
    filenames = os.listdir(item_type_plural)
    if len(filenames) > 0:
      filenames = [x for x in filenames if x.find('.xml') > 0 and x.find('_comments.') <= 0 and x.find('_autosave.') <= 0]
      filenames.sort(key = lambda x: os.path.getmtime(item_type_plural+'/'+x), reverse=True)
      
      latest_item = None
      count = 0
      while latest_item == None and count < len(filenames):
        latest_file = filenames[count]
        latest_item = load_item(item_type, latest_file)
        if latest_item.draft == True:
          latest_item = None
        else:
          latest_items.append(latest_item)
        count+=1 # check the next latest item
          
  return latest_items

def load_items_by_type(item_type, offset=0):
  items = []
  filename_timestamps = {}
  
  if offset < 0: offset = 0
  
  item_type_plural = item_types_plural[item_type]
  filenames = os.listdir(item_type_plural)
  filenames = [x for x in filenames if x.find('.xml') > 0 and x.find('_comments.') <= 0 and x.find('_autosave.') <= 0]
  
  for filename in filenames:
    filepath = item_type_plural+'/'+filename
    filename_timestamps[os.path.getmtime(filepath)] = filename
  
  timestamps = list(filename_timestamps.keys())
  timestamps.sort()
  timestamps.reverse()
  
  i=0
  for timestamp in timestamps:
    if i-offset >= options['items_per_page']: break
    if i >= offset:
      items.append(load_item(item_type, filename_timestamps[timestamp]))
    i += 1
  return items


def load_items_all(offset=0, limit=options['items_per_page']):
  items = []
  filename_timestamps = {}
  
  if offset < 0: offset = 0
  
  for item_type in item_types:
    if item_type == 'page': continue
    item_type_plural = item_types_plural[item_type]
    filenames = os.listdir(item_type_plural)
 
    for filename in filenames:
      filepath = item_type_plural+'/'+filename
      if filename.find('_comments.') > 0: continue  # skip comments
      if filename.find('_autosave.') > 0: continue  # skip autosaved files
      filename_timestamps[os.path.getmtime(filepath)] = (item_type,filename)
  
  timestamps = list(filename_timestamps.keys())
  timestamps.sort()
  timestamps.reverse()
  
  i=0
  for timestamp in timestamps:
    if i-offset >= limit: break
    if i >= offset:
      items.append(load_item(filename_timestamps[timestamp][0],filename_timestamps[timestamp][1]))
    i += 1
  return items
  
  
def check_login(session_id=None):
  c = web.cookies(s_id=session_id)
  sess = session.Session(c.s_id)
  sys.stderr.write(repr(sess.info))
  if 'logged_in' in sess.info:  # already logged in
    sess.save() # update timestamp
  else:                               # not logged in - check password
    i = web.input(login_name='',login_password='')
    sys.stderr.write(str(i))
    if i.login_name == credentials[0] and i.login_password == credentials[1]:
      sess.info['logged_in'] = True
      sess.save() # update session
      web.setcookie('s_id', sess.id, expires='')
  return sess


def get_item_fields():
  item_fields = {}
  for item_type in item_types:
    temp_item = item_modules[item_type].new('')
    item_field_names = [var for var in temp_item.__dict__ if not var in temp_item.hidden]
 
    if 'sorted' in temp_item.__dict__:
      item_field_names.sort(key = lambda x: temp_item.sorted.index(x))
 
    item_fields[item_type] = item_field_names
  return item_fields
  
def generate_site_menu():
  results = ''
  results += '<li><a href="'+options['base_url']+'/">Latest</a></li>\n'
  for item_type in item_types:
    if item_type == 'page': continue
    item_type_plural = item_types_plural[item_type]
    results += '<li><a href="'+options['base_url']+'/view/'+item_type+'">'+item_type_plural.capitalize()+'</a></li>\n'
  results += '<li><a href="'+options['base_url']+'/about">About</a></li>\n'
  return results
  
def generate_basic_js():
  item_fields = get_item_fields()
  results = ''
  results += 'base_url = \''+options['base_url']+'\';\n'
  results += 'item_types = '+simplejson.dumps(item_types)+';\n'
  results += 'item_fields = '+simplejson.dumps(item_fields)+';\n'
  results += 'rightnow = '+str(int(time.time()))+';\n'
  results += 'connect(window, \'onload\', this, \'blog_my_onload\');\n'

  return results
  
def get_comment_hashcodes():
  c = web.cookies(comments='')
  return c.comments.split(',')

def str2bool(s):
  if str(s).lower() == 'false':
    return False
  else:
    return bool(s)
  
def get_item_url(item_type, item_id):
  if item_type == 'page':
    return options['base_url']+'/'+item_id
  return options['base_url']+'/view/'+item_id

def feed_wrap(item, contents):
  headline = ''
  updated = time.strftime('%Y-%b-%mT%H:%M:%S%Z', time.gmtime(item.timestamp))

  results = '''
 <entry>
   <title>%(headline)s</title>
   <link href="%(link)s"/>
   <id>%(link)s</id>
   <updated>%(updated)s</updated>
   <content type="xhtml" xml:lang="en" xml:base="http://diveintomark.org/">
     %(contents)s
   </content>
 </entry>
'''%{'headline':headline,
     'link':options['base_url']+'/view/'+item.id,
     'contents':contents,
     'updated':updated}
  return results
  
def get_filedata(path='files'):
  filenames = os.listdir(path)
  filedata = []
  subdir = path.strip('files/')
  
  for filename in filenames:
    filepath = path+'/'+filename
    timestamp = os.path.getmtime(filepath)
    if os.path.isdir(filepath):
      filedata.append({'name':filename,'timestamp':timestamp})
      filedata.extend(get_filedata(path+'/'+filename))
    else:
      statinfo = os.stat(filepath)
      filesize = statinfo[stat.ST_SIZE]      
      filedata.append({'name':filename,'timestamp':timestamp,'size':filesize,'subdir':subdir})
  return filedata
  
def exclude_drafts(items):
  return [x for x in items if x.draft != True]
  
def drafts_only(items):
  return [x for x in items if x.draft == True]

class default:
  def GET(self, name):
    javascript = ''
    main_stuff = ''
    title = options['site_title']

    setup()
    site_menu = generate_site_menu()
    site_menu += '<li class="feed_link"><a href="'+options['base_url']+'/view/all?feed=1"><img src="'+options['base_url']+'/feed_icon.png" alt="feed"/></a></li>'

    sess = check_login()
    if sess.param('logged_in') == True:
      javascript += 'logged_in = true;\n'
        
    latest_items = load_latest_item_of_each_type()
    item_ids = []
    
    latest_items.sort(key = lambda x: x.timestamp)
    latest_items.reverse()
    
    for latest_item in latest_items:
      if latest_item.__class__.__name__ == 'page': continue
      main_stuff += latest_item.render('short', {'headline':'Latest '+latest_item.__class__.__name__})
      item_ids.append(latest_item.id)
      
    javascript += generate_basic_js()
    javascript += 'item_ids = '+simplejson.dumps(item_ids)+';\n'

    web.header("Content-Type","text/html; charset=utf-8")
    print(render(main_stuff,site_menu,javascript,options['base_url'],title))
    
    
class view_page:
  def GET(self, page_id):
    javascript = ''
    main_stuff = ''
    title = ''

    setup()
    site_menu = generate_site_menu()
    sess = check_login()
    if sess.param('logged_in') == True:
      javascript += 'logged_in = true;\n'
    
    pattern = re.compile( '\W')
    page_id = pattern.sub('',page_id) # remove non-alphanumeric
    
    p = load_page(page_id)
    if p:
      title = p.getTitle()
      p_comments = load_comments(page_id, 'page')
      
      main_stuff += p.render()
      if not p.disable_comments:
        main_stuff += '<div id="add_comment"></div>'
      main_stuff += ''.join([c.render() for c in p_comments])
      
      editable_comments = []
      comment_hashcodes = get_comment_hashcodes()
      for c in p_comments:
        if c.hashcode in comment_hashcodes:
          editable_comments.append(c.id)
      javascript += 'editable_comments = '+simplejson.dumps(editable_comments)+';\n'
      javascript += 'comment_ids = '+simplejson.dumps([c.id for c in p_comments])+';\n'

    else:
      main_stuff += '<div id="create_this_page" class="header_button" style="display:none;">Create page "'+page_id+'"!</div>'
      main_stuff += '<br/><br/>Page "'+page_id+'" does not exist!'
    
    javascript += 'page_id = \''+page_id+'\';\n'
    javascript += generate_basic_js()

    web.header("Content-Type","text/html; charset=utf-8")
    print(render(main_stuff,site_menu,javascript,options['base_url'],title))
    
    
class view:
  def GET(self, item_type_or_id):
    javascript = ''
    main_stuff = ''
    title = ''
    single_item = True  # False = multiple items of a type
    
    i = web.input(offset=0,feed=False)

    setup()
    site_menu = generate_site_menu()
    site_menu += '<li class="feed_link"><a href="?feed=1"><img src="'+options['base_url']+'/feed_icon.png" alt="feed"/></a></li>'

    sess = check_login()
    if sess.param('logged_in') == True:
      javascript += 'logged_in = true;\n'
    
    options['debug'] = True
    
    # check for item or type (also check plural types)
    if item_type_or_id == 'all':
      single_item = False
      item_types_plural[item_type_or_id] = 'items'
    elif item_type_or_id == 'drafts':
      single_item = False
      item_types_plural[item_type_or_id] = 'items'
    else:
      for item_type in item_types:
        if item_type_or_id == item_type:
          single_item = False
          break
        if item_type_or_id == item_types_plural[item_type]:
          item_type_or_id = item_type
          single_item = False
          break
          
    if single_item:
      item = load_item_by_id(item_type_or_id)[0]
      if item == None:
        main_stuff = 'Not found'
      else:
        title = item.getTitle()

        item_comments = load_comments(item_type_or_id)
        
        main_stuff = item.render()
        
        if not item.disable_comments:
          main_stuff += '<div id="add_comment"></div>'
        
        main_stuff += ''.join([c.render() for c in item_comments])
        
        javascript += generate_basic_js()
        javascript += 'item_ids = '+simplejson.dumps([item.id])+';\n'
        javascript += 'comment_ids = '+simplejson.dumps([c.id for c in item_comments])+';\n'
        
        editable_comments = []
        comment_hashcodes = get_comment_hashcodes()
        for comment in item_comments:
          if comment.hashcode in comment_hashcodes:
            editable_comments.append(comment.id)
        javascript += 'editable_comments = '+simplejson.dumps(editable_comments)+';\n'
        
    else: # multiple items
      offset = int(i.offset)

      if item_type_or_id == 'all':
        items = load_items_all(offset)
        items = exclude_drafts(items)
      elif item_type_or_id == 'drafts':
        items = load_items_all(offset, 999999)
        items = drafts_only(items)
      else:
        items = load_items_by_type(item_type_or_id, offset)
        items = exclude_drafts(items)
      
      javascript += generate_basic_js()
      javascript += 'item_ids = '+simplejson.dumps([item.id for item in items])+';\n'
      
      nav_stuff = ''
      if offset > 0:
        nav_stuff += '<a href="'+options['base_url']+'/view/'+item_type_or_id+'?offset='+str(offset-10)+'"> Newer '+item_types_plural[item_type_or_id]+'</a>\n'
      
      if len(items) == options['items_per_page']:
        nav_stuff += '<a href="'+options['base_url']+'/view/'+item_type_or_id+'?offset='+str(offset+10)+'"> Older '+item_types_plural[item_type_or_id]+'</a>\n'
       
      if not nav_stuff == '':
        nav_stuff = '<div class="nav">'+nav_stuff+'</div>'
       
      main_stuff += nav_stuff
      
      title = item_types_plural[item_type_or_id] + ' ' + str(offset+1) + ' - ' + str(offset+10)

      for item in items:
        rendered = item.render('short')
        if i.feed:
          main_stuff += feed_wrap(item, rendered)
        else:
          main_stuff += rendered

    try:
      main_stuff = main_stuff.encode('utf-8', 'replace')
    except UnicodeDecodeError:
      main_stuff = str(main_stuff,'utf-8', 'replace')
      
    
    if i.feed:
      web.header("Content-Type","application/atom+xml; charset=utf-8")
      print('''
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

 <title>%(title)s</title>
 <link href="%(link)s"/>
 <id></id>
 
%(main_stuff)s
</feed>      
      
      
''' % {'title':options['base_url'],'link':options['base_url'],'main_stuff':main_stuff})
    else:
      web.header("Content-Type","text/html; charset=utf-8")
      print(render(main_stuff,site_menu,javascript,options['base_url'],title))
    
class preview:
  def POST(self):
    javascript = ''
    main_stuff = ''
    site_menu = ''
    title = 'preview'

    setup()

    i = web.input('__item_type__')
    item_type = i.__item_type__
    item_type_plural = item_types_plural[item_type]
    new_id = ''
    
    if item_type == 'page':  # page
      new_id = i.__id__
    else:
      new_id = str(get_max_id()+1)

    new_item = item_modules[item_type].new(new_id)
    i.pop('__item_type__')
 
    for k in i:  # convert input to unicode
      i[k] = str(str(i[k]),'utf-8', 'replace')
 
    new_item.__dict__.update(i)
    main_stuff = new_item.render()
    
    web.header("Content-Type","text/html; charset=utf-8")
    print(render(main_stuff,site_menu,javascript,options['base_url'],title))
    
    
class get_item:
  def GET(self, item_id):
    javascript = ''
    main_stuff = ''
    results = {}

    setup()
    
    if item_id.isdigit():
      (item, item_type) = load_item_by_id(item_id)
    else:
      item_type = 'page'
      item = load_page(item_id)
     
    if item:
      results['item'] = item.toweb()
      autosaved_item = load_autosave_item(item_type,item_id)
      if autosaved_item:
        results['autosaved'] = autosaved_item.toweb()
    
    javascript += simplejson.dumps(results)+'\n'

    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(javascript)
    
class get_files:
  def GET(self):
    javascript = ''
    main_stuff = ''
    results = {}

    setup()
    filedata = get_filedata()
    javascript += simplejson.dumps({'success':True,'files':filedata})+'\n'

    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(javascript)
    
class upload_file:
  def POST(self,sid,subdir):
    javascript = ''
    main_stuff = ''
    results = {}
    
    setup()
    sess = check_login(sid)
    
    #FILE = open('files/upload.log', 'w')
    #fcntl.flock(FILE, fcntl.LOCK_EX)
    #FILE.write('input: '+str(web.input())+'\n')
    #FILE.write('cookies: '+str(web.cookies())+'\n')
    #FILE.write('subdir: '+subdir+'\n')
    #fcntl.flock(FILE, fcntl.LOCK_UN)
    #FILE.close()
    
    if sess.param('logged_in') == True:
      i = web.input('Filedata','Filename')
      filename = i.Filename
      filedata = i.Filedata
      
      filepath = 'files/'+filename
      
      if not subdir == '':
        p = re.compile('\W')
        subdir = p.sub('',subdir) 

        if not os.path.exists('files/'+subdir):
          os.mkdir('files/'+subdir)
        filepath = 'files/'+subdir+'/'+filename
      
      FILE = open(filepath, 'wb')
      fcntl.flock(FILE, fcntl.LOCK_EX)
      FILE.write(filedata)
      fcntl.flock(FILE, fcntl.LOCK_UN)
      FILE.close()
 
      filedata = get_filedata()
      javascript += simplejson.dumps({'success':True,'files':filedata})+'\n'

    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(javascript)

class move_files:
  def POST(self):
    javascript = ''
    main_stuff = ''
    results = {}
    
    setup()
    sess = check_login()
    
    #FILE = open('files/upload.log', 'w')
    #fcntl.flock(FILE, fcntl.LOCK_EX)
    #FILE.write('move_files input: '+str(web.input())+'\n')
    #fcntl.flock(FILE, fcntl.LOCK_UN)
    #FILE.close()
    
    if sess.param('logged_in') == True: 
      i = web.input('files','subdir')
      files = i.files.split(',')
      subdir = i.subdir
      
      if not os.path.isdir('files/'+subdir):
        os.mkdir('files/'+subdir)
      
      for f in files:
        shutil.move('files/'+f,'files/'+subdir+'/'+f)
      
      filedata = get_filedata()
      javascript += simplejson.dumps({'success':True,'files':filedata})+'\n'

    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(javascript)



class delete_file:
  def POST(self):
    javascript = ''
    messages = []
    results = {}
    filedata = {}
    success = False
    
    setup()
    sess = check_login()
    
    if sess.param('logged_in') == True:
      success = True
      i = web.input('name',subdir='')
      filename = i.name
      subdir = i.subdir
      if subdir == '':
        if os.path.isfile('files/'+filename):
          os.remove('files/'+filename)
      elif os.path.isfile('files/'+subdir+'/'+filename):
        os.remove('files/'+subdir+'/'+filename)
      else:
        success = False
        messages.append('[E] File not found!')
        
      # delete empty subdirs
      filenames = os.listdir('files')
      for filename in filenames:
        if os.path.isdir('files/'+filename):
          subfiles = os.listdir('files/'+filename)
          if len(subfiles) == 0:
            os.rmdir('files/'+filename)
        
      filedata = get_filedata()
    else:
      messages.append('[E] Not logged in!')
      
    results.update({'success':str(success).lower(),'messages':messages,'files':filedata})
    
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps(results))
   

class get_comment:
  def GET(self, item_id, comment_id):
    javascript = ''
    main_stuff = ''

    setup()
    item_comments = load_comments(item_id)
    
    for comment in item_comments:
      if str(comment.id) == str(comment_id):
        javascript += simplejson.dumps(comment.toweb())+'\n'
        break
    
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(javascript)


class do_login:
  def POST(self, name):
    success = False
    sess = check_login()
    if sess.param('logged_in') == True:
      success = True
      web.setcookie('s_id', sess.id, expires='0')
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower()}))


    
class add_item:
  def POST(self):
    messages = []
    results = {}
    
    setup()
    i = web.input('__item_type__',__disable_comments__=False,__draft__=False)
    item_type = i.__item_type__
    disable_comments = str2bool(i.__disable_comments__)
    draft = str2bool(i.__draft__)

    success = False
    sess = check_login()
    if not sess.param('logged_in'):
      success = False
      messages.append('[E] Not logged in!')
    else:
      item_type_plural = item_types_plural[item_type]
      
      new_id = ''
      if item_type == 'page':  # page
        new_id = i.__id__
        i.pop('__id__')
      else:
        new_id = str(get_max_id()+1)

      new_item = item_modules[item_type].new(str(new_id))
      new_item.disable_comments = disable_comments
      new_item.draft = draft
 
      i.pop('__item_type__')
      i.pop('__disable_comments__')
      i.pop('__draft__')
 
      new_item.__dict__.update(i)
 
      filename = item_type+'_'+new_id+'.xml'
      new_item.save(item_type_plural+'/'+filename)
 
      text = ','.join(i)
      messages.append('[I] Added new '+item_type+' ('+new_id+')! ('+text+')')
      success = True
      results['item_id'] = new_item.id
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    results.update({'success':str(success).lower(),'messages':messages})
    print(simplejson.dumps(results))
    


class update_item:
  def POST(self):
    messages = []
    results = {}
    
    setup()
    i = web.input('__id__',__autosave__=False,__disable_comments__=False,__preserve_timestamp__=False,__draft__=False)
    item_id = i.__id__
    
    disable_comments = str2bool(i.__disable_comments__)
    preserve_timestamp = str2bool(i.__preserve_timestamp__)
    draft = str2bool(i.__draft__)
      
    success = False
    sess = check_login()
    if not sess.param('logged_in'):
      success = False
      messages.append('[E] Not logged in!')
    else:

      item = load_item_by_id(item_id)[0]
      if item == None:
        success = False
        messages.append('[E] Item not found')
      else:
        item_type = item.__class__.__name__
        item_type_plural = item_types_plural[item_type]
        item.disable_comments = disable_comments
        item.draft = draft
        
        i.pop('__id__')
        i.pop('__disable_comments__')
        i.pop('__preserve_timestamp__')
        i.pop('__draft__')

        item.__dict__.update(i)
 
        filename = item_type+'_'+item.id+'.xml'
        autosave_filename = item_type+'_'+item.id+'_autosave.xml'
        if item_type == 'page':
          autosave_filename = item.id+'_autosave.xml'
 
        if i.__autosave__ == '1':
          item.save(item_type_plural+'/'+autosave_filename)
        else:
          item.save(item_type_plural+'/'+filename)
          
          if preserve_timestamp == True:
            os.utime(item_type_plural+'/'+filename, (time.time(), int(item.timestamp)))
          
          if os.path.isfile(item_type_plural+'/'+autosave_filename):
            os.remove(item_type_plural+'/'+autosave_filename)
 
          text = ','.join(i)
          messages.append('[I] Updated '+item_type+' '+str(item.id)+'! ('+text+')')
          success = True
          results['item_id'] = item.id
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    results.update({'success':str(success).lower(),'messages':messages})
    print(simplejson.dumps(results))


class delete_item:
  def POST(self):
    messages = []
    success = False
    
    setup()
    i = web.input('id')
    item_id = i.id

    deleted = False    
    
    for item_type in item_types:
      item_type_plural = item_types_plural[item_type]
      filename = item_type_plural+'/'+item_type+'_'+item_id+'.xml'
      if os.path.isfile(filename):
        os.remove(filename)
        autosave_filename = item_type_plural+'/'+item_type+'_'+item_id+'_autosave.xml'
        if os.path.isfile(autosave_filename):
          os.remove(autosave_filename)
        deleted = True
        
    filename = 'pages/'+item_id+'.xml'
    if os.path.isfile(filename):
      os.remove(filename)
      autosave_filename = 'pages/'+item.id+'_autosave.xml'
      if os.path.isfile(autosave_filename):
        os.remove(autosave_filename)
      deleted = True
    
    if deleted:
      success = True
      messages.append('[I] Item '+item_id+' deleted.')
    else:
      messages.append('[I] Unable to delete item '+item_id+' - not found')
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower(),'messages':messages}))
    
class delete_autosave_item:
  def POST(self):
    messages = []
    success = False
    
    setup()
    i = web.input('id')
    item_id = i.id

    deleted = False    
    
    for item_type in item_types:
      item_type_plural = item_types_plural[item_type]
      autosave_filename = item_type_plural+'/'+item_type+'_'+item_id+'_autosave.xml'
      if item_type == 'page':
        autosave_filename = item_type_plural+'/'+item_type+'_autosave.xml'
      
      if os.path.isfile(autosave_filename):
        os.remove(autosave_filename)
        deleted = True
    
    if deleted:
      success = True
      messages.append('[I] Autosave file for item '+item_id+' deleted.')
    else:
      messages.append('[I] Unable to delete autosave file for item '+item_id+' - not found')
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower(),'messages':messages}))
  
      
class add_comment:
  def POST(self):
    messages = []
    success = False
    comment_hashcodes = get_comment_hashcodes()
    
    setup()
    i = web.input('item_id','text',by='Anonymous',link='',t=0)
    item_id = i.item_id
    
    for k in i:  # convert input to unicode
      i[k] = str(str(i[k]),'utf-8', 'replace')
    
    (item, item_type) = load_item_by_id(item_id)
    item_comments = load_comments(item_id, item_type)

    new_comment = comments.comment()
    new_comment.id = int(comments.get_max_id(item_comments))+1
    new_comment.text = i.text
    new_comment.by = i.by
    new_comment.link = i.link
    new_comment.item_id = i.item_id
    
    valid = True
    
    # lame-o spam protection.  Probably have to make this more complex later.
    rightnow = int(time.time())
    if rightnow - int(i.t) > 86400:
      valid = False
    
    # disallow blank comments
    p = re.compile('\S')
    if not p.match(new_comment.text):
      valid = False
    
    if valid:
      item_comments.append(new_comment)
      save_comments(item_id,item_type,item_comments)
      comment_hashcodes.append(new_comment.hashcode)
      web.setcookie('comments', ','.join([c for c in comment_hashcodes]), expires='')

      if options['update_email']:
        SENDMAIL = "/usr/sbin/sendmail" # sendmail location
        p = os.popen("%s -t" % SENDMAIL, "w")
        p.write('To: '+options['update_email']+'\n')
        p.write('Subject: comment added to '+options['base_url']+'\n\n')
        
        comment_urladdress = '#item_'+item_id+'_comment_'+str(new_comment.id)

        email_text = '''
%(submitter)s posted a comment to item "%(item_id)s".
View it here:
%(link)s

or read it below:

%(text)s
''' % {'submitter':new_comment.by+' '+new_comment.link,'item_id':item_id,'link':get_item_url(item_type, item_id)+comment_urladdress,'text':new_comment.text}
        
        p.write(email_text)
        sts = p.close()

    success = True
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower(),'new_comment_id':new_comment.id,'messages':messages,'comment_html':new_comment.render()}))

class update_comment:
  def POST(self):
    messages = []
    success = False
    comment_hashcodes = get_comment_hashcodes()
    
    setup()
    sess = check_login()

    i = web.input('item_id','comment_id')
    item_id = i.item_id
    comment_id = i.comment_id
    
    for k in i:  # convert input to unicode
      i[k] = str(str(i[k]),'utf-8', 'replace')

    (item, item_type) = load_item_by_id(item_id)
    item_comments = load_comments(item_id, item_type)
    
    comment_to_update = None
    for comment in item_comments:
      if str(comment.id) == str(comment_id):
        if comment.hashcode in comment_hashcodes or sess.param('logged_in') == True:
          comment_to_update = comment
    
    if comment_to_update:
      comment_to_update.text = i.text
      comment_to_update.by = i.by
      comment_to_update.link = i.link
      save_comments(item_id,item_type,item_comments)
    
    success = True
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower(),'messages':messages,'comment_html':comment_to_update.render()}))



class delete_comment:
  def POST(self):
    messages = []
    success = False
    comment_hashcodes = get_comment_hashcodes()
    
    setup()
    sess = check_login()

    i = web.input('item_id','comment_id')
    item_id = i.item_id
    comment_id = i.comment_id

    (item, item_type) = load_item_by_id(item_id)
    item_comments = load_comments(item_id, item_type)
    
    comment_to_delete = None
    for comment in item_comments:
      if str(comment.id) == str(comment_id):
        if comment.hashcode in comment_hashcodes or sess.param('logged_in') == True:
          comment_to_delete = comment
          break
    
    if comment_to_delete:
      item_comments.remove(comment_to_delete)
      save_comments(item_id,item_type,item_comments)
    
    success = True
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower(),'messages':messages}))



class do_logout:
  def POST(self, name):
    success = True
    sess = check_login()
    if sess.param('logged_in') == True:
      sess.delete()
      web.setcookie('s_id', sess.id, expires='')
      
    web.header("Content-Type",options['json_mime_type']+"; charset=utf-8")
    print(simplejson.dumps({'success':str(success).lower()}))

def runfcgi_apache(func):
  web.wsgi.runfcgi(func, None)

if options['debug'] == True:
  web.webapi.internalerror = web.debugerror
  
if options['fastcgi'] == True:
  web.wsgi.runwsgi = runfcgi_apache

render = web.template.frender('blog_my.html')

def basic():
    web.run(urls,globals())

if __name__ == "__main__":
    basic()
    #web.run(urls,globals(),web.profiler)
