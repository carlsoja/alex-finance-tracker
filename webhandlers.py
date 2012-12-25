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

def CleanKeyName(key_name):
  key_name = key_name.replace(' ', '-').replace('&', '-').replace('--', '-')
  key_name = key_name.replace('--', '-').lower()
  return key_name

def DeleteExpense(key_name):
  # get expense from DB and store amount
  expense = mydb.Expense.get_by_key_name(key_name)
  amount = expense.amount
  # edit account balance if has account (not a tax/deduction)
  if expense.account:
    account = db.get(expense.account)
    if account.a_type == 'Credit Card':
      account.unv_balance -= expense.amount
      if expense.verified:
        account.ver_balance -= expense.amount
    else:
      account.unv_balance += expense.amount
      if expense.verified:
        account.ver_balance += expense.amount
    account.put()
  # find in and delete from paycheck expenses list
  if expense.paycheck:
    paycheck = db.get(expense.paycheck)
    expense_type = ''
    if expense.key() == paycheck.federal_income_tax:
      expense_type = 'deduction'
      paycheck.federal_income_tax = None
    elif expense.key() == paycheck.state_income_tax:
      expense_type = 'deduction'
      paycheck.state_income_tax = None
    elif expense.key() in paycheck.other_taxes:
      expense_type = 'deduction'
      paycheck.other_taxes.remove(expense.key()) # TEST THIS LIST REMOVAL!!!
    elif expense.key() in paycheck.ins_deductions:
      expense_type = 'deduction'
      paycheck.ins_deductions.remove(expense.key()) # TEST THIS LIST REMOVAL!!!
    elif expense.key() in paycheck.other_deductions:
      expense_type = 'deduction'
      paycheck.other_deductions.remove(expense.key()) # TEST THIS LIST REMOVAL!!!
    elif expense.key() in paycheck.expenses:
      paycheck.expenses.remove(expense.key()) # TEST THIS LIST REMOVAL!!!
    # edit paycheck balances
    paycheck.final_balance += amount
    if expense_type == 'deduction':
      paycheck.after_deduction_balance += amount
      paycheck.after_deposit_balance += amount
    # delete expense and put new paycheck/account data into DB
    db.delete(expense.key())
    if account:
      account.put()
    if paycheck:
      paycheck.put()

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
    
    # get all payment accounts (checking and credit card)
    payment_accounts = db.GqlQuery('SELECT * '
                                   'FROM Account '
                                   'WHERE a_type IN (\'Checking\', \'Credit Card\') '
                                   'ORDER BY a_type ASC')

    # get all parent categories
    parent_categories = db.GqlQuery('SELECT * '
                                    'FROM Category '
                                    'WHERE has_subcats = True '
                                    'ORDER BY name ASC')
    # get all child categories
    child_categories = db.GqlQuery('SELECT * '
                                   'FROM Category '
                                   'WHERE has_subcats = False')
    # put child categories in groups list with same order as parent categories list
    child_cats_groups = []
    for cat in parent_categories: # loop through parent categories
      # create list of sub-cats with parent cat = parent cat currently being looped through
      sub_cat_list = [x for x in child_categories if x.parent_cat.key() == cat.key()]
      if len(sub_cat_list) != 0:
        child_cats_groups.append(sub_cat_list)
		
    template_values = { 'expenses': u_expenses,
                        'paychecks': a_paychecks,
                        'accounts': accounts,
                        'total': account_total,
                        'payment_accounts': payment_accounts,
                        'parent_cats': parent_categories,
                        'child_cat_groups': child_cats_groups }
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
    # get current paycheck data
    path = self.request.path
    p_key = db.Key(path.split('/')[-1])
    paycheck = db.get(p_key)
    
    # set taxes template variables
    other_taxes = []
    tax_total = 0
    if paycheck.federal_income_tax:
      tax_total += paycheck.federal_income_tax.amount
    if paycheck.state_income_tax:
      tax_total += paycheck.state_income_tax.amount
    for tax_key in paycheck.other_taxes:
      other_taxes.append(db.get(tax_key))
      tax_total += db.get(tax_key).amount

    # set deductions template variables
    deductions_total = 0
    med_deduct = ''
    dental_deduct = ''
    life_deduct = ''
    vis_deduct = ''
    d_401k = ''
    for ins_key in paycheck.ins_deductions:
      ins_entity = db.get(ins_key)
      deductions_total += ins_entity.amount
      if ins_entity.e_category == 'Medical':
        med_deduct = ins_entity
      elif ins_entity.e_category == 'Dental':
        dental_deduct = ins_entity
      elif ins_entity.e_category == 'Life':
        life_deduct = ins_entity
      elif ins_entity.e_category == 'Vision':
        vis_deduct = ins_entity
    if paycheck.ret_401k:
      d_401k = paycheck.ret_401k
      deductions_total += paycheck.ret_401k.amount
    other_deductions = []
    for deduct_key in paycheck.other_deductions:
      other_deductions.append(db.get(deduct_key))
      deductions_total += db.get(deduct_key).amount
    
    # set deposits template variables
    accounts = db.GqlQuery('SELECT * '
                           'FROM Account '
                           'WHERE a_type != \'Checking\'')
    deposits = []
    deposits_total = 0
    for deposit_key in paycheck.deposits:
      deposits.append(db.get(deposit_key))
      deposits_total += db.get(deposit_key).amount
    
    # set expenses template variables
    # get all payment accounts (checking and credit card)
    payment_accounts = db.GqlQuery('SELECT * '
                                   'FROM Account '
                                   'WHERE a_type IN (\'Checking\', \'Credit Card\') '
                                   'ORDER BY a_type ASC')
    
    # get all parent categories
    parent_categories = db.GqlQuery('SELECT * '
                                    'FROM Category '
                                    'WHERE has_subcats = True '
                                    'ORDER BY name ASC')
    # get all child categories
    child_categories = db.GqlQuery('SELECT * '
                                   'FROM Category '
                                   'WHERE has_subcats = False')
    # put child categories in groups list with same order as parent categories list
    child_cats_groups = []
    for cat in parent_categories: # loop through parent categories
      # create list of sub-cats with parent cat = parent cat currently being looped through
      sub_cat_list = [x for x in child_categories if x.parent_cat.key() == cat.key()]
      if len(sub_cat_list) != 0:
        child_cats_groups.append(sub_cat_list)

    expenses = []
    expenses_total = 0
    food_expenses = []
    food_expenses_total = 0
    gas_expenses = []
    gas_expenses_total = 0
    all_expenses_total = 0
    for expense_key in paycheck.expenses:
      expense = db.get(expense_key)
      if expense.parent_e_category.name == 'Food & Dining':
        food_expenses.append(expense)
        food_expenses_total += expense.amount
      elif expense.child_e_category.name == 'Gas':
        gas_expenses.append(expense)
        gas_expenses_total += expense.amount
      else:
        expenses.append(expense)
        expenses_total += expense.amount
      all_expenses_total += expense.amount
    
    # send all variables to template and display
    template_values = { 'paycheck': paycheck,
                        'federal_tax': paycheck.federal_income_tax,
                        'state_tax': paycheck.state_income_tax,
                        'other_taxes': other_taxes,
                        'tax_total': tax_total,
                        'med_insurance': med_deduct,
                        'dental_insurance': dental_deduct,
                        'life_insurance': life_deduct,
                        'vision_insurance': vis_deduct,
                        '401k': d_401k,
                        'deductions': other_deductions,
                        'deductions_total': deductions_total,
                        'accounts': accounts,
                        'deposits': deposits,
                        'deposits_total': deposits_total,
                        'payment_accounts': payment_accounts,
                        'parent_cats': parent_categories,
                        'child_cat_groups': child_cats_groups,
                        'expenses': expenses,
                        'expenses_total': expenses_total,
                        'food_expenses': food_expenses,
                        'food_expenses_total': food_expenses_total,
                        'gas_expenses': gas_expenses,
                        'gas_expenses_total': gas_expenses_total,
                        'all_expenses_total': all_expenses_total }
    path = os.path.join(os.path.dirname(__file__), 'templates/paycheckdetail.tpl')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    path = self.request.path
    p_key = db.Key(path.split('/')[-1])
    paycheck = db.get(p_key)
    
    if self.request.get('tax-type') is not '':
      key_name = paycheck.date.isoformat() + '-' + self.request.get('tax-type')
      if self.request.get('tax-type') in ['federal', 'state']:
        key_name += 'income-tax'
      else:
        key_name += '-' + self.request.get('tax-name') + '-tax'
      new_tax = mydb.Expense(key_name=key_name)
      # retrieve and set tax data
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
      # put updated paycheck entity into DB
      paycheck.put()
    
    deduction_type = self.request.get('deduction-type')
    if deduction_type is not '':
      deduction_name = self.request.get('deduction-name')
      deduction_amount = self.request.get('deduction-amount')
      key_name = paycheck.date.isoformat() + '-'
      if deduction_type == 'other':
        key_name += 'other-' + deduction_name
      else:
        key_name += deduction_type
      key_name += '-deduction'
      new_deduction = mydb.Expense(key_name=key_name)
      new_deduction.date = paycheck.date
      new_deduction.amount = float(deduction_amount)
      new_deduction.account = None
      new_deduction.paycheck = p_key
      if deduction_type == 'other':
        new_deduction.frequency = 'One-Time'
        new_deduction.e_category = 'Other Deduction'
      else:
        new_deduction.freqency = 'Core'
        new_deduction.e_category = deduction_type
      if deduction_type == 'other':
        new_deduction.name = deduction_name
      else:
        if deduction_type == '401k':
          new_deduction.name = '401k Contribution'
        else:
          new_deduction.name = deduction_type
          new_deduction.name += ' Insurance Deduction'
      new_deduction.put()
      deduction = mydb.Expense.get_by_key_name(key_name)
      # adjust paycheck values
      if deduction_type == 'other':
        paycheck.other_deductions.append(deduction.key())
      elif deduction_type == '401k':
        paycheck.ret_401k = deduction.key()
      else:
        paycheck.ins_deductions.append(deduction.key())
      paycheck.after_deduction_balance -= deduction.amount
      paycheck.after_deposit_balance -= deduction.amount
      paycheck.final_balance -= deduction.amount
      # put updated paycheck entity into DB
      paycheck.put()
    
    deposit_account = self.request.get('deposit-account')
    if deposit_account is not '':
      # get account entity from retrieved key_name
      account_db = mydb.Account.get_by_key_name(deposit_account)
      # set new deposit entity key_name
      deposit_amount = self.request.get('deposit-amount')
      deposit_description = self.request.get('deposit-description')
      key_name = paycheck.date.isoformat() + '-'
      key_name += deposit_account
      key_name += '-deposit'
      # create new deposit entity with key_name and set entity data
      new_deposit = mydb.Transfer(key_name=key_name)
      new_deposit.date = DateFromString(self.request.get('deposit-date'))
      new_deposit.amount = float(deposit_amount)
      new_deposit.description = deposit_description
      new_deposit.account = None
      new_deposit.receiving_account = account_db.key()
      new_deposit.paycheck = p_key
      new_deposit.frequency = 'Regular'
      new_deposit.name = deposit_account + ' - ' + paycheck.date.isoformat() + ' Paycheck Deposit'
      new_deposit.verified = False
      new_deposit.put()
      deposit = mydb.Transfer.get_by_key_name(key_name)
      # adjust paycheck values
      paycheck.deposits.append(deposit.key())
      paycheck.after_deposit_balance -= deposit.amount
      paycheck.final_balance -= deposit.amount
      # put updated paycheck entity into DB
      paycheck.put()
      # adjust account balances
      account_db.unv_balance += deposit.amount
      account_db.ver_balance += deposit.amount
      # put updated account entity into DB
      account_db.put()
    
    expense_vendor = self.request.get('expense-vendor')
    if expense_vendor is not '':
      # get account entity from retrieved key_name
      expense_account = self.request.get('expense-account')
      account_db = mydb.Account.get_by_key_name(expense_account)
      # set new expense entity key_name
      expense_amount = self.request.get('expense-amount')
      expense_description = self.request.get('expense-description')
      expense_date = self.request.get('expense-date')
      key_name = expense_date + '-' + expense_vendor + '-' + str(expense_amount)
      key_name = CleanKeyName(key_name)
      # create new expense entity with key_name and set entity data
      new_expense = mydb.Expense(key_name=key_name)
      new_expense.date = DateFromString(expense_date)
      new_expense.vendor = expense_vendor
      new_expense.amount = float(expense_amount)
      new_expense.description = expense_description
      new_expense.account = account_db.key()
      new_expense.paycheck = p_key
      new_expense.frequency = 'One-Time'
      new_expense.name = expense_date + ' - ' + expense_vendor + ' - ' + expense_amount
      new_expense.verified = False
      new_expense.paid = False
      parent_cat = self.request.get('parent-cat')
      child_cat_name = 'child-' + parent_cat
      child_cat = self.request.get(child_cat_name)
      parent_db = mydb.Category.get_by_key_name(parent_cat)
      new_expense.parent_e_category = parent_db.key()
      if child_cat == '':
        new_expense.child_e_category = None
        logging.info('NO CHILD CAT')
      else:
        child_db = mydb.Category.get_by_key_name(child_cat)
        new_expense.child_e_category = child_db.key()
      new_expense.put()
      expense = mydb.Expense.get_by_key_name(key_name)
      # adjust paycheck values
      paycheck.expenses.append(expense.key())
      paycheck.final_balance -= expense.amount
      # put updated paycheck entity into DB
      paycheck.put()
      # adjust account unverified balance
      account_db.unv_balance += expense.amount
      # put updated account entity into DB
      account_db.put()
    
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
		account.ver_balance = float(self.request.get('starting'))
		account.last_verified = DateFromString(self.request.get('last_verified'))
		
		account.put()
		
		self.redirect(self.request.url)

class CreateCategories(webapp2.RequestHandler):
  def get(self):
    q = db.GqlQuery('SELECT * '
                    'FROM Category ')
                    
    parent_cats = []
    sub_cats = []
    for cat in q:
      if cat.has_subcats:
        parent_cats.append(cat)
      else:
        sub_cats.append(cat)
    
    template_values = { 'parent_cats': parent_cats,
                        'sub_cats': sub_cats }
    path = os.path.join(os.path.dirname(__file__), 'templates/category.tpl')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    key_name = self.request.get('name') + '-' + self.request.get('p-c') + '-' + 'cat'
    key_name = CleanKeyName(key_name)
    category = mydb.Category(key_name=key_name)
    
    category.id = self.request.get('name').lower().replace(' ', '-')
    category.name = self.request.get('name')
    category.type = self.request.get('type')
    if self.request.get('p-c') == 'child':
      category.has_subcats = False
      category.is_subcat = True
      category.parent_cat = db.get(self.request.get('parent_cat'))
    else:
      category.has_subcats = True
      category.is_subcat = False
    
    category.put()
    
    self.redirect(self.request.url)