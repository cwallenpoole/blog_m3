import re, urllib.request, urllib.parse, urllib.error, string, random
import web

def merge(d1, d2): # merges two dictionaries - duplicate keys are overwritten
  d3 = d1.copy()
  d3.update(d2)
  return d3


def GenRandomString(length=8, chars=string.ascii_letters + string.digits):
  return ''.join([random.choice(chars) for i in range(length)])


def xml_quick_extract_old(data, tag_name):
  # it doesn't get any dumber than this.  ignores attributes, element order, fooled by duplicate tag names at different depths.
  results = "";
  p = re.compile('<'+ tag_name + '>(.+?)<\/'+ tag_name + '>', re.S)
  iterator = p.finditer(data)
  for match in iterator:
    results += urllib.parse.unquote_plus(match.group(1))
  return results
  
def xml_quick_extract(data, tag_name):
  # it doesn't get any dumber than this.  ignores attributes, element order, fooled by duplicate tag names at different depths.
  results = []
  try:
    data = bytes(data, 'utf-8')
  except:
    pass
  p = '<'+ tag_name + '>(.+?)<\/'+ tag_name + '>'
  p = re.compile(bytes(p, 'utf-8'), re.S)
  iterator = p.finditer(data)
  import sys
  for match in iterator:
    g = match.group(1).decode('utf-8')
    sys.stderr.write(g)
    results.append(urllib.parse.unquote_plus(g))
  if len(results) == 0: results = ['']
  return results
  
def insert_filerefs(contents):
  p = re.compile('\{\{(.+?)\}\}', re.S)
  #iterator = p.finditer(data)
  results = re.sub(p,fileref2link,contents);
  return results

def fileref2link(match):
  #return '<img src="/files/'+match.group(1)+'"/>'
  #if isimage(match.group(1)):
  #  return '!['+match.group(1)+'](%(base_url)s/files/'+match.group(1)+')'
  #else:
  #  return '['+match.group(1)+'](%(base_url)s/files/'+match.group(1)+')'
  
  fileref = match.group(1)
  fileref = fileref.replace('<em>','_')
  fileref = fileref.replace('</em>','_')
    
  if isimage(fileref):
    return '<img class="img" src="%(base_url)s/files/'+fileref+'" alt="'+fileref+'"/>'
  else:
    return '<a href="%(base_url)s/files/'+fileref+'">'+fileref+'</a>'


def wiki2html(contents):
  results = web.safemarkdown(contents)
  if not results:
    return ''
  return results
  
def isimage(fname):
  p = re.compile('\.(gif|jpe?g|png|)$', re.S)
  if p.search(fname):
    return True
  return False
  
def wikiparse(contents, base_url=''):
  results = ''

  if contents.find('<html>') < 0:
    results = wiki2html(contents)
  else:
    p = re.compile('(.*?)<html>(.+?)<\/html>(.*?)', re.S)
    iterator = p.finditer(contents)
    for match in iterator:
      results += wiki2html(match.group(1))+match.group(2)+wiki2html(match.group(3))
   
    p = re.compile('.*<\/html>(.*)', re.S)
    iterator = p.finditer(contents)
    for match in iterator:
      results += wiki2html(match.group(1))

  results = results.replace('%','%%')
  results = insert_filerefs(results)
  results = results % {'base_url':base_url}
  return results

def strip_tags(text):
  p = re.compile('<\/?.+?>', re.S)
  results = re.sub(p,'',text);
  return results
  
def strip_nonhtml(text):
  p = re.compile('<(\/?)html>', re.S)
  results = re.sub(p,'--\\1html--',text);
  results = strip_tags(results)
  p = re.compile('--(\/?)html--', re.S)
  results = re.sub(p,'<\\1html>',results);
  return results

def strip_comments(text):
  p = re.compile('<!\-\-.*?\-\->', re.S)
  results = re.sub(p,'',text);
  return results

def strip_script(text):
  p = re.compile('<script>.+?<\/script>', re.S)
  results = re.sub(p,'',text);
  return results

  
def sentence_chop(text, chop_length):
  results = text
  months_abv = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec")
  
  if len(results) > chop_length:
    for month_abv in months_abv:
      results = re.sub('\\b('+month_abv+')\.','\\1',results) # remove periods after month abbreviations so they aren't flagged as sentence ends.

    p = re.compile('(.{'+str(chop_length)+'}.+?\.\s+).+', re.S)
    results = re.sub(p,'\\1',results);
     
    for month_abv in months_abv:
      results = re.sub('\\b('+month_abv+')\\b','\\1.',results)      # add periods back to month abbreviations
  return results

def close_tags(data):
  results = data
  tag_stack = []
  
  p = re.compile('<(/?\w+?)(\s.+?)?>', re.S)
  iterator = p.finditer(data)
  for match in iterator:
    if match.group(1)[0] == '/':  #closing tag
      if tag_stack[-1] == match.group(1)[1:]:
        tag_stack.pop()
    else:                         # opening tag
      tag_stack.append(match.group(1))
  
  tag_stack.reverse()
  for tag in tag_stack:
    results += '</'+tag+'>'
  
  return results
