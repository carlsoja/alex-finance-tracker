#usr/bin/python2.7

import db as mydb
import datetime
import logging
import os
import webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template

def DateFromString(date):
	new_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	return datetime.date(new_date.year, new_date.month, new_date.day)

class MainPage(webapp2.RequestHandler):
	def get(self):
		u_expenses = db.GqlQuery('SELECT * FROM Expense WHERE paycheck = NULL ORDER BY date')
		a_paychecks = db.GqlQuery('SELECT * FROM Paycheck WHERE closed = FALSE ORDER BY date')
		
		template_values = { 'expenses': u_expenses,
		                    'paychecks': a_paychecks }
		path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		expense = mydb.Expense()
		
		expense.date = DateFromString(self.request.get('date'))
		expense.name = self.request.get('name')
		expense.description = self.request.get('description')
		expense.amount = float(self.request.get('amount'))
		expense.frequency = self.request.get('freq')
		expense.e_category = self.request.get('category')
		
		expense.put()
		
		u_expenses = db.GqlQuery('SELECT * FROM Expense WHERE paycheck = NULL ORDER BY date')
		a_paychecks = db.GqlQuery('SELECT * FROM Paycheck WHERE closed = FALSE ORDER BY date')
		
		template_values = { 'expenses': u_expenses,
		                    'paychecks': a_paychecks }
		path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
		self.response.out.write(template.render(path, template_values))

class CreatePaycheck(webapp2.RequestHandler):
	def get(self):
		q = db.GqlQuery('SELECT * '
		                'FROM Paycheck ')
		
		template_values = { 'paychecks': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/paycheck.tpl')
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		paycheck = mydb.Paycheck()
		
		paycheck.date = DateFromString(self.request.get('date'))
		paycheck.gross = float(self.request.get('gross'))
		if self.request.get('current') == 'True':
			paycheck.current = True
		else:
			paycheck.current = False
		if self.request.get('closed') == 'True':
			paycheck.closed = True
		else:
			paycheck.closed = False
		
		paycheck.put()
		
		q = db.GqlQuery('SELECT * '
		                'FROM Paycheck ')
		
		template_values = { 'paychecks': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/paycheck.tpl')
		self.response.out.write(template.render(path, template_values))