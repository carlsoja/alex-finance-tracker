#usr/bin/python2.7

import webapp2
import webhandlers

application = webapp2.WSGIApplication([
    ('/', webhandlers.MainPage),
    ('/paycheck', webhandlers.CreatePaycheck)
    ], debug=True)