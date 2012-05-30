import sys, os

options = {}
options['site_title'] = 'My Site!'                                      # default site title
item_types = ['post','book','quote']                              	# types of items for the site
credentials = ('me','12345')                                     	# the username & password for the site
options['update_email'] = 'your_email@something.com'                  	# set to "None" for none
options['domain'] = 'http://' + os.environ['HTTP_HOST']                            # the address of the site
options['subdir'] = 'blog_my'
options['items_per_page'] = 10                                    	# number of items to show per page (when viewing multiple items of the same type)
options['json_mime_type'] = 'text/plain'                                # because the JSON mime-type hasn't condensed to a standard yet.  This might change to text/x-json or application/json at some point.
options['debug'] = False                                           		# show debugging output
options['fastcgi'] = False                                      		# run as fastCGI
options['base_url'] = options['domain'] + '/' + options['subdir'] if options['subdir'] else options['domain']
