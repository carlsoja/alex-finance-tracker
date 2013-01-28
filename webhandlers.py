#usr/bin/python2.7

import db as mydb
import datetime
import logging
import os
import webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):
  def get(self):
    template_values = { 'expenses': mydb.Expense.GetUnassignedExpenses(),
                        'paychecks': mydb.Paycheck.GetOpenPaychecks(),
                        'accounts': mydb.Account.GetAllAccounts(),
                        'total': mydb.Account.GetTotalUnvBalanceFromAllAccounts(),
                        'payment_accounts': mydb.Account.GetAllPaymentAccounts(),
                        'parent_cats': mydb.Category.GetAllParentCats(),
                        'child_cat_groups': mydb.Category.GetChildCatGroupings() }
    path = os.path.join(os.path.dirname(__file__), 'templates/home.tpl')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    # if description is present, assume adding a new expense
    if self.request.get('expense-vendor') is not '':
      parent_key = self.request.get('parent-cat')
      child_key = self.request.get('child-' + parent_key)
      # store post data and use to create new expense entity
      kwargs = {'vendor': self.request.get('expense-vendor'),
                'date': self.request.get('expense-date'),
                'name': self.request.get('expense-name'),
                'description': self.request.get('expense-description'),
                'amount': self.request.get('expense-amount'),
                'account': self.request.get('expense-account'),
                'frequency': 'One-Time',
                'parent-cat': parent_key,
                'child-cat': child_key}
      mydb.Expense.CreateNewExpense(**kwargs)
    # otherwise, attach selected expense(s) to paycheck
    else:
			# get paycheck entity from retrieved paycheck key
			paycheck = mydb.Paycheck.get_by_key_name(self.request.get('paycheck'))
			# see if expense was selected and assign to selected paycheck
			for index, expense in enumerate(mydb.Expense.GetUnassignedExpenses()):
				# construct expense form selection label
				e_label = 'expense' + str(index + 1)
				# if that expense selection label was selected
				if self.request.get(e_label):
					# attach expense to paycheck
					paycheck.AttachUnassignedExpense(self.request.get(e_label))
		
    logging.info('Redirecting to: ' + self.request.url)
    self.redirect(self.request.url)

class CreatePaycheck(webapp2.RequestHandler):
	def get(self):
		template_values = { 'paychecks': mydb.Paycheck.GetOpenPaychecks(),
		                    'accounts': mydb.Account.GetAllCheckingSavingsAccounts() }
		path = os.path.join(os.path.dirname(__file__), 'templates/paycheck.tpl')
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		# create new paycheck entity and save to DB
		paycheck_args = {'date': self.request.get('date'),
		                 'account': self.request.get('account'),
		                 'gross': self.request.get('gross'),
		                 'current': self.request.get('current'),
		                 'closed': self.request.get('closed')}
		paycheck = mydb.Paycheck.CreateNewPaycheck(**paycheck_args)
		
		logging.info('Redirecting to: ' + self.request.url)
		self.redirect(self.request.url)

class PaycheckDetail(webapp2.RequestHandler):
  def get(self):
    # get current paycheck
    p_key = db.Key(self.request.path.split('/')[-1])
    paycheck = db.get(p_key)
    
    # send all variables to template and display
    template_values = { 'paycheck': paycheck,
                        'federal_tax': paycheck.GetFederalIncomeTax(),
                        'state_tax': paycheck.GetStateIncomeTax(),
                        'other_taxes': paycheck.GetOtherTaxes(),
                        'tax_total': paycheck.GetTaxTotal(),
                        'med_insurance': paycheck.GetMedicalDeduction(),
                        'dental_insurance': paycheck.GetDentalDeduction(),
                        'life_insurance': paycheck.GetLifeDeduction(),
                        'vision_insurance': paycheck.GetVisionDeduction(),
                        '401k': paycheck.ret_401k,
                        'deductions': paycheck.GetOtherDeductions(),
                        'deductions_total': paycheck.GetDeductionsTotal(),
                        'accounts': mydb.Account.GetAllNonCheckingAccounts(),
                        'deposits': paycheck.GetAllOtherDeposits(),
                        'deposits_total': paycheck.GetOtherDepositsTotal(),
                        'transfers': paycheck.GetAllTransfers(),
                        'transfers_total': paycheck.GetTransfersTotal(),
                        'payment_accounts': mydb.Account.GetAllPaymentAccounts(),
                        'parent_cats': mydb.Category.GetAllParentCats(),
                        'child_cat_groups': mydb.Category.GetChildCatGroupings(),
                        'food_expenses': paycheck.GetAllFoodExpenses(),
                        'food_expenses_total': paycheck.GetFoodExpensesTotal(),
                        'other_expenses': paycheck.GetAllMiscExpenses(),
                        'other_expenses_total': paycheck.GetMiscExpensesTotal(),
                        'all_expenses_total': paycheck.GetExpensesTotal() }
    path = os.path.join(os.path.dirname(__file__), 'templates/paycheckdetail.tpl')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    # TODO: Determine original account for paycheck deposits (use checking account?)
    path = self.request.path
    p_key = db.Key(path.split('/')[-1])
    paycheck = db.get(p_key)
    
    if self.request.get('delete-key') is not '':
      paycheck.RemoveTransaction(self.request.get('delete-key'))
    elif self.request.get('verify-key') is not '':
      to_verify = mydb.Transaction.GetTransaction(self.request.get('verify-key'))
      to_verify.Verify()
    elif self.request.get('tax-type') is not '':
      tax_args = {'date': paycheck.date.isoformat(),
                  'amount': self.request.get('tax-amount'),
                  'tax-type': self.request.get('tax-type'),
                  'name': self.request.get('tax-name') }
      paycheck.AddNewTax(**tax_args)
    elif self.request.get('deduction-type') is not '':
      deduct_args = {'date': paycheck.date.isoformat(),
                     'amount': self.request.get('deduction-amount'),
                     'deduct-type': self.request.get('deduction-type'),
                     'name': self.request.get('deduction-name') }
      paycheck.AddNewDeduction(**deduct_args)
    elif self.request.get('deposit-source') is not '':
      deposit_args = {'date': self.request.get('deposit-date'),
                      'amount': self.request.get('deposit-amount'),
                      'source': self.request.get('deposit-source'),
                      'description': self.request.get('deposit-description')}
      paycheck.AddNewDeposit(**deposit_args)
    elif self.request.get('transfer-account') is not '':
      rec_account_keyname = self.request.get('transfer-account')
      transfer_args = {'date': paycheck.date.isoformat(),
                       'amount': self.request.get('transfer-amount'),
                       'origin-account': paycheck.dest_account,
                       'rec-account': mydb.Account.get_by_key_name(rec_account_keyname),
                       'description': self.request.get('transfer-description')}
      paycheck.AddNewTransfer(**transfer_args)
    elif self.request.get('expense-vendor') is not '':
      account_key = self.request.get('expense-account')
      parent_key = self.request.get('parent-cat')
      child_key = self.request.get('child-' + parent_key)
      expense_args = {'date': paycheck.date.isoformat(),
                      'amount': self.request.get('expense-amount'),
                      'vendor': self.request.get('expense-vendor'),
                      'description': self.request.get('expense-description'),
                      'account': mydb.Account.get_by_key_name(account_key),
                      'frequency': 'One-Time',
                      'paycheck': paycheck,
                      'parent-cat': mydb.Category.get_by_key_name(parent_key),
                      'child-cat': mydb.Category.get_by_key_name(child_key)}
      paycheck.AddNewExpense(**expense_args)
    
    logging.info('Redirecting to: ' + self.request.url)
    self.redirect(self.request.url)

class CreateAccount(webapp2.RequestHandler):
	def get(self):
	  template_values = { 'accounts': mydb.Account.GetAllAccounts() }
	  path = os.path.join(os.path.dirname(__file__), 'templates/account.tpl')
	  self.response.out.write(template.render(path, template_values))
		
	def post(self):
	  account_args = {'name': self.request.get('name'),
	                  'type': self.request.get('type'),
	                  'starting': self.request.get('starting'),
	                  'start-date': self.request.get('start_date'),
	                  'last-verified': self.request.get('last_verified')}
	  mydb.Account.CreateNewAccount(**account_args)
	  
	  logging.info('Redirecting to: ' + self.request.url)
	  self.redirect(self.request.url)

class AccountDetail(webapp2.RequestHandler):
  def get(self):
    # get account
    a_key = db.Key(self.request.path.split('/')[-1])
    account = db.get(a_key)
    
    transaction_data = account.GetRecentTransactionBalanceList()
    
    template_values = {'account': account,
                       'transactions': transaction_data[0],
                       'starting': transaction_data[1]}
    path = os.path.join(os.path.dirname(__file__), 'templates/accountdetail.tpl')
    self.response.out.write(template.render(path, template_values))

class CreateCategories(webapp2.RequestHandler):
  def get(self):
    template_values = { 'parent_cats': mydb.Category.GetAllParentCats(),
                        'sub_cats': mydb.Category.GetAllChildCats() }
    path = os.path.join(os.path.dirname(__file__), 'templates/category.tpl')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    parent = ''
    if self.request.get('parent-cat') is not '':
      parent = db.get(self.request.get('parent-cat'))
    cat_args = {'name': self.request.get('name'),
                'p/c': self.request.get('p-c'),
                'type': self.request.get('type'),
                'parent': parent}
    mydb.Category.CreateNewCategory(**cat_args)
    
    logging.info('Redirecting to: ' + self.request.url)
    self.redirect(self.request.url)