#usr/bin/python2.7

import db as mydb
import logging
import os
import webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):
	def get(self):
		q = db.GqlQuery('SELECT * '
		                'FROM Expense ')
		
		template_values = { 'expenses': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		expense = mydb.Expense()
		
		expense.date = self.request.get('date')
		expense.name = self.request.get('name')
		expense.description = self.request.get('description')
		expense.amount = float(self.request.get('amount'))
		expense.frequency = self.request.get('freq')
		expense.e_category = self.request.get('category')
		
		expense.put()
		
		q = db.GqlQuery('SELECT * '
		                'FROM Expense ')
		
		template_values = { 'expenses': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
		self.response.out.write(template.render(path, template_values))