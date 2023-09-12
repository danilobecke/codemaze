chdir = 'code'
wsgi_app = 'app_debug:server'
bind = '0.0.0.0:3031'
workers = 2
threads = 2
max_requests = 1000
reload = True
