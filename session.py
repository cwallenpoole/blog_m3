import string,os,random,pickle

from blog_my_lib import GenRandomString
    
class Session:

#    $sid = $cgi->cookie("CGISESSID") || undef;
#    $session    = new CGI::Session(undef, $sid, {Directory=>'/tmp'}); 

#    $session = new CGI::Session("driver:File", undef, {Directory=>"/tmp"});

  def __init__(self, id, args={}):
    self.id = id
    self.directory = './sessions'
    self.filename = ''
    self.info = {'expires':86400}
    
    if 'directory' in args:
      self.directory = args['directory']
    
    # if sessions directory doesn't exist, create it
    if not os.path.isdir(self.directory):
      os.mkdir(self.directory)
    
    # compute id
    if self.id == None:  
      # new id.  Create new sessions file.
      self.id = GenRandomString(8)
      self.filename = self.directory+'/session_'+self.id
    else:                
      # caller-supplied id.  Check sessions file.
      self.filename = self.directory+'/session_'+self.id
      if os.path.isfile(self.filename):
        self.load()
        
  def load(self):
    try:
      FILE = open(self.filename,"rb")
      self.info = pickle.load(FILE)
      FILE.close()
    except Exception:
      return None
   
  def save(self):
    FILE = open(self.filename,"wb")
    pickle.dump(self.info, FILE)
    FILE.close()
    
  def delete(self):
    os.remove(self.filename)
    self.info = {}
    
  def param(self, key):
    if key in self.info:
      return self.info[key]
    return None
  
  
  
      
      
  
      

