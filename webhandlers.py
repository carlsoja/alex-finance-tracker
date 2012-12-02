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
    a_paychecks = db.GqlQuery('SELECT * FROM Paycheck WHERE closed = FALSE ORDER BY date DESC')
    accounts = db.GqlQuery('SELECT * FROM Account')
    
    account_total = 0
    for account in accounts:
      if account.a_type != 'Credit Card':
        account_total += account.unv_balance
      else:
        account_total -= account.unv_balance
		
    template_values = { 'expenses': u_expenses,
                        'paychecks': a_paychecks,
                        'accounts': accounts,
                        'total': account_total }
    path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    u_expenses = db.GqlQuery('SELECT * FROM Expense WHERE paycheck = NULL ORDER BY date')
    # if description is present, assume adding a new expense
    if self.request.get('description'):
      # set new key name and create new expense entity
      key_name = self.request.get('date') + '-' + self.request.get('name')
      expense = mydb.Expense(key_name=key_name)
      # retrieve and set expense data
      expense.date = DateFromString(self.request.get('date'))
      expense.name = self.request.get('name')
      expense.description = self.request.get('description')
      expense.amount = float(self.request.get('amount'))
      expense.account = db.Key(self.request.get('account'))
      expense.frequency = self.request.get('freq')
      expense.e_category = self.request.get('category')
      # get account entity and adjust unverified balance
      account = db.get(expense.account)
      if account.a_type == 'Credit Card':
        account.unv_balance += expense.amount
      else:
        account.unv_balance -= expense.amount
		  # put new account and expense entities into datastore
      account.put()
      expense.put()
    else:
			# get paycheck entity from retrieved paycheck key
			p_key = db.Key(self.request.get('paycheck'))
			paycheck = db.get(p_key)
			# see if expense was selected and assign to selected paycheck
			for index, expense in enumerate(u_expenses):
				# construct expense form selection label
				e_label = 'expense' + str(index + 1)
				# if that expense selection label was selected
				if self.request.get(e_label):
					# get expense entity from retrieve expense key
					e_key = db.Key(self.request.get(e_label))
					expense = db.get(e_key)
					# assign paycheck key to expense entity
					expense.paycheck = p_key
					# add expense key to paycheck entity expense list
					paycheck.expenses.append(e_key)
					# decrement expense amount from final paycheck balance
					paycheck.final_balance -= expense.amount
					# put new expense/paycheck/account entities into datastore
					expense.put()
					paycheck.put()
					account.put()

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
		key_name = self.request.get('date') + '-' + str(self.request.get('gross'))
		paycheck = mydb.Paycheck(key_name=key_name)
		
		paycheck.date = DateFromString(self.request.get('date'))
		paycheck.gross = float(self.request.get('gross'))
		paycheck.after_deduction_balance = paycheck.gross
		paycheck.after_deposit_balance = paycheck.gross
		paycheck.final_balance = paycheck.gross
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

class PaycheckDetail(webapp2.RequestHandler):
  def get(self):
    path = self.request.path
    logging.info(path)
    p_key = db.Key(path.split('/')[-1])
    paycheck = db.get(p_key)
    
    other_taxes = []
    tax_total = 0
    if paycheck.federal_income_tax:
      tax_total += paycheck.federal_income_tax.amount
    if paycheck.state_income_tax:
      tax_total += paycheck.state_income_tax.amount
    for tax_key in paycheck.other_taxes:
      other_taxes.append(db.get(tax_key))
      tax_total += db.get(tax_key).amount
    deductions = []
    deductions_total = 0
    for deduct_key in paycheck.deductions:
      deductions.append(db.get(deduct_key))
      deductions_total += db.get(deduct_key).amount
    deposits = []
    deposits_total = 0
    for deposit_key in paycheck.deposits:
      deposits.append(db.get(deposit_key))
      deposits_total += db.get(deposit_key).amount
    expenses = []
    expenses_total = 0
    for expense_key in paycheck.expenses:
      expenses.append(db.get(expense_key))
      expenses_total += db.get(expense_key).amount
    
    template_values = { 'paycheck': paycheck,
                        'federal_tax': paycheck.federal_income_tax,
                        'state_tax': paycheck.state_income_tax,
                        'other_taxes': other_taxes,
                        'tax_total': tax_total,
                        'deductions': deductions,
                        'deductions_total': deductions_total,
                        'deposits': deposits,
                        'deposits_total': deposits_total,
                        'expenses': expenses,
                        'expenses_total': expenses_total }
    path = os.path.join(os.path.dirname(__file__), 'templates/paycheckdetail.tpl')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    path = self.request.path
    logging.info(path)
    p_key = db.Key(path.split('/')[-1])
    paycheck = db.get(p_key)
    
    if self.request.get('tax-type'):
      if self.request.get('tax-type') in ['federal', 'state']:
        key_name = paycheck.date.isoformat() + '-' + self.request.get('tax-type') + 'income-tax'
      else:
        key_name = paycheck.date.isoformat() + '-' + self.request.get('tax-type')
        key_name += '-' + self.request.get('tax-name')
      new_tax = mydb.Expense(key_name=key_name)
      # retrieve and set tax expense data
      new_tax.date = paycheck.date
      new_tax.amount = float(self.request.get('tax-amount'))
      new_tax.account = None
      new_tax.frequency = 'Core'
      new_tax.e_category = 'Taxes'
      new_tax.paycheck = p_key
      if self.request.get('tax-type') == 'federal':
        new_tax.name = 'Federal Income Tax'
      elif self.request.get('tax-type') == 'state':
        new_tax.name = 'State Income Tax'
      else:
        new_tax.name = self.request.get('tax-name')
      new_tax.put()
      tax = mydb.Expense.get_by_key_name(key_name)
      # adjust paycheck values
      if self.request.get('tax-type') == 'federal':
        paycheck.federal_income_tax = tax.key()
      elif self.request.get('tax-type') == 'state':
        paycheck.state_income_tax = tax.key()
      else:
        paycheck.other_taxes.append(tax.key())
      paycheck.after_deduction_balance -= tax.amount
      paycheck.after_deposit_balance -= tax.amount
      paycheck.final_balance -= tax.amount
      # put new tax expense and updated paycheck entity into DB
      paycheck.put()
    
    logging.info('Redirecting to: ' + self.request.url)
    self.redirect(self.request.url)

class CreateAccount(webapp2.RequestHandler):
	def get(self):
		q = db.GqlQuery('SELECT * '
		                'FROM Account')
		
		template_values = { 'accounts': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/account.tpl')
		self.response.out.write(template.render(path, template_values))
		
	def post(self):
		key_name = self.request.get('name') + '-' + self.request.get('type')
		account = mydb.Account(key_name=key_name)
		
		account.name = self.request.get('name')
		account.a_type = self.request.get('type')
		account.unv_balance = float(self.request.get('starting'))
		account.last_verified = DateFromString(self.request.get('last_verified'))
		
		account.put()
		
		q = db.GqlQuery('SELECT * '
		                'FROM Account')
		
		template_values = { 'accounts': q }
		path = os.path.join(os.path.dirname(__file__), 'templates/account.tpl')
		self.response.out.write(template.render(path, template_values))