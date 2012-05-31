#!/usr/local/bin/python3
import sys
stdout = sys.stdout
try:
  import blog_my

  blog_my.basic()
except Exception as e:
  import traceback
  stdout.write('''Content-Type: text/html

<html><head></head><body>
I'm sorry. Something seems to have gone HORRIBLY wrong. I can't figure out what I am supposed to do!
</body></html>''')
