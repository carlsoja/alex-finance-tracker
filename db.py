#usr/bin/python2.7

import logging

from datetime import date
from datetime import datetime
from datetime import timedelta
from google.appengine.ext import db

class Account(db.Model):
	name = db.StringProperty()
	a_type = db.StringProperty(
	  choices = set(['Checking', 'Savings', 'Investment', 'Credit Card']))
	unv_balance = db.FloatProperty()
	ver_balance = db.FloatProperty()
	start_date = db.DateProperty()
	last_verified = db.DateProperty()
	
	"""
	Account keyname format: "<name>-<type>-account"
	"""
	@staticmethod
	def CreateKeyname(name, type):
	  key_name = name + '-'
	  key_name += type + '-'
	  key_name += 'account'
	  return CleanKeyName(key_name)
	
	@staticmethod
	def CreateNewAccount(**kwargs):
	  # create new account entity
	  key_name = Account.CreateKeyname(kwargs['name'], kwargs['type'])
	  a = Account(key_name=key_name)
	  a.name = kwargs['name']
	  a.a_type = kwargs['type']
	  a.unv_balance = float(kwargs['starting'])
	  a.ver_balance = a.unv_balance
	  a.start_date = DateFromString(kwargs['start-date'])
	  a.last_verified = DateFromString(kwargs['last-verified'])
	  # create new PaycheckAccountBalance entities for every paycheck after account start date
	  future_paychecks = Paycheck.GetAllPaychecksAfterDate(a.start_date)
	  for p in future_paychecks:
	    p_a = PaycheckAccountBalance.CreatePaycheckAccountBalance(a, p, a.ver_balance)
	  return db.get(a.put())
	
	@classmethod
	def GetAllAccounts(cls):
	  return cls.all()
	
	@classmethod
	def GetAllPaymentAccounts(cls):
	  return cls.all().filter('a_type IN', ['Checking', 'Credit Card']).order('a_type')
	
	@classmethod
	def GetAllNonCheckingAccounts(cls):
	  return cls.all().filter('a_type !=', 'Checking')
	
	@classmethod
	def GetAllCheckingSavingsAccounts(cls):
	  return cls.all().filter('a_type IN', ['Checking', 'Savings'])
	
	@classmethod
	def GetActiveAccountsAfterDate(cls, start_date):
	  date_to_use = DateFromString(start_date)
	  return cls.all().filter('start_date <=', date_to_use)
	
	@classmethod
	def GetTotalUnvBalanceFromAllAccounts(cls):
	  total = 0
	  for a in cls.GetAllAccounts():
	    if a.a_type != 'Credit Card':
	      total += a.unv_balance
	    else:
	      total -= a.unv_balance
	  return total
	
	def GetAllExpensesFromAccount(self):
	  try:
	    return self.account_expenses.order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllUnverifiedExpensesFromAccount(self):
	  try:
	    return self.account_expenses.filter('verified =', False).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedExpensesFromAccount(self):
	  try:
	    return self.account_expenses.filter('verified =', True).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedExpensesFromAccountAfterDate(self, date):
	  try:
	    q = self.account_expenses.filter('verified =', True)
	    return q.filter('date >', DateFromString(date)).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllDepositsFromAccount(self):
	  try:
	    return self.account_deposits.order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllUnverifiedDepositsFromAccount(self):
	  try:
	    return self.account_deposits.filter('verified =', False).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedDepositsFromAccount(self):
	  try:
	    return self.account_deposits.filter('verified =', True).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedDepositsFromAccountAfterDate(self, date):
	  try:
	    q = self.account_deposits.filter('verified =', True)
	    return q.filter('date >', DateFromString(date)).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllTransfersOriginatingFromAccount(self):
	  try:
	    return self.transfers_origin.order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllUnverifiedTransfersOriginatingFromAccount(self):
	  try:
	    return self.transfers_origin.filter('verified =', False).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedTransfersOriginatingFromAccount(self):
	  try:
	    return self.transfers_origin.filter('verified =', True).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedTransfersOriginatingFromAccountAfterDate(self, date):
	  try:
	    q = self.transfers_origin.filter('verified =', True)
	    return q.filter('date >', DateFromString(date)).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllTransfersReceivedIntoAccount(self):
	  try:
	    return self.transfers_receiving.order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllUnverifiedTransfersReceivedIntoAccount(self):
	  try:
	    return self.transfers_receiving.filter('verified =', False).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedTransfersReceivedIntoAccount(self):
	  try:
	    return self.transfers_receiving.filter('verified =', True).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def GetAllVerifiedTransfersReceivingIntoAccountAfterDate(self, date):
	  try:
	    q = self.transfers_receiving.filter('verified =', True)
	    return q.filter('date >', DateFromString(date)).order('-date').fetch(100)
	  except IndexError:
	    return None
	
	def CalculateBalanceAfterDate(self, date):
	  balance = self.ver_balance
	  expenses = self.GetAllVerifiedExpensesFromAccountAfterDate(date)
	  deposits = self.GetAllVerifiedDepositsFromAccountAfterDate(date)
	  origin_transfers = self.GetAllVerifiedTransfersOriginatingFromAccountAfterDate(date)
	  receiving_transfers = self.GetAllVerifiedTransfersReceivingIntoAccountAfterDate(date)
	  
	  for e in expenses:
	    balance += e.amount
	  for d in deposits:
	    balance -= d.amount
	  for o in origin_transfers:
	    balance += o.amount
	  for r in receiving_transfers:
	    balance -= r.amount
	  
	  return balance
	
	def GetRecentUnvTransactionBalanceList(self):
	  start_date = date.today()
	  current_date = start_date
	  unv_balance = self.unv_balance
	  
	  u_expenses = self.GetAllUnverifiedExpensesFromAccount()
	  u_origin_transfers = self.GetAllUnverifiedTransfersOriginatingFromAccount()
	  u_receiving_transfers = self.GetAllUnverifiedTransfersReceivedIntoAccount()
	  u_deposits = self.GetAllUnverifiedDepositsFromAccount()
	  
	  t_list = []
	  e_index = 0
	  t_o_index = 0
	  t_r_index = 0
	  d_index = 0
	  if len(u_expenses) == 0: e_end = True
	  else: e_end = False
	  if len(u_origin_transfers) == 0: t_o_end = True
	  else: t_o_end = False
	  if len(u_receiving_transfers) == 0: t_r_end = True
	  else: t_r_end = False
	  if len(u_deposits) == 0: d_end = True
	  else: d_end = False
	  # unverified transactions to t_list in date/type order
	  while((e_end and t_o_end and t_r_end and d_end) != True):
	    logging.info('TEST: ' + str(e_end and t_o_end and t_r_end and d_end))
	    try:
	      if e_end != True and u_expenses[e_index].date == current_date:
	        t_list.append((u_expenses[e_index], unv_balance))
	        unv_balance += u_expenses[e_index].amount
	        e_index += 1
	        logging.info('e_index: '+ str(e_index) + ', len: ' + str(len(u_expenses)))
	        if e_index == len(u_expenses):
	          e_end = True
	        continue
	    except IndexError:
	      pass
	    try:
	      if t_o_end != True and u_origin_transfers[t_o_index].date == current_date:
	        t_list.append((u_origin_transfers[t_o_index], unv_balance))
	        unv_balance += u_origin_transfers[t_o_index].amount
	        t_o_index += 1
	        logging.info('t_o_index: '+ str(t_o_index) + ', len: ' + str(len(u_origin_transfers)))
	        if t_o_index == len(u_origin_transfers):
	          t_o_end = True
	        continue
	    except IndexError:
	      pass
	    try:
	      if t_r_end != True and u_receiving_transfers[t_r_index].date == current_date:
	        t_list.append((u_receiving_transfers[t_r_index], unv_balance))
	        unv_balance -= u_receiving_transfers[t_r_index].amount
	        t_r_index += 1
	        logging.info('t_r_index: '+ str(t_r_index) + ', len: ' + str(len(u_receiving_transfers)))
	        if t_r_index == len(u_receiving_transfers):
	          t_r_end = True
	        continue
	    except IndexError:
	      pass
	    try:
	      if d_end != True and u_deposits[d_index].date == current_date:
	        t_list.append((u_deposits[d_index], unv_balance))
	        unv_balance -= u_deposits[d_index].amount
	        d_index += 1
	        logging.info('d_index: '+ str(d_index) + ', len: ' + str(len(u_deposits)))
	        if d_index == len(u_deposits):
	          d_end = True
	        continue
	    except IndexError:
	      pass
	    current_date -= timedelta(days=1)
	  return (t_list, unv_balance)
	
	def GetRecentVerTransactionBalanceList(self, days=60):
	  start_date = date.today()
	  end_date = start_date - timedelta(days=days)
	  current_date = start_date
	  unv_balance = self.unv_balance
	  ver_balance = self.ver_balance
	  
	  v_expenses = self.GetAllVerifiedExpensesFromAccount()
	  v_origin_transfers = self.GetAllVerifiedTransfersOriginatingFromAccount()
	  v_receiving_transfers = self.GetAllVerifiedTransfersReceivedIntoAccount()
	  v_deposits = self.GetAllVerifiedDepositsFromAccount()
	  
	  t_list = []
	  e_index = 0
	  t_o_index = 0
	  t_r_index = 0
	  d_index = 0
	  # add verified transactions to t_list in date/type order
	  while(current_date >= end_date):
	    try:
	      if v_expenses[e_index].date == current_date:
	        t_list.append((v_expenses[e_index], ver_balance))
	        ver_balance += v_expenses[e_index].amount
	        e_index += 1
	        continue
	    except IndexError:
	      pass
	    try:
	      if v_origin_transfers[t_o_index].date == current_date:
	        t_list.append((v_origin_transfers[t_o_index], ver_balance))
	        ver_balance += v_origin_transfers[t_o_index].amount
	        t_o_index += 1
	        continue
	    except IndexError:
	      pass
	    try:
	      if v_receiving_transfers[t_r_index].date == current_date:
	        t_list.append((v_receiving_transfers[t_r_index], ver_balance))
	        ver_balance -= v_receiving_transfers[t_r_index].amount
	        t_r_index += 1
	        continue
	    except IndexError:
	      pass
	    try:
	      if v_deposits[d_index].date == current_date:
	        t_list.append((v_deposits[d_index], ver_balance))
	        ver_balance -= v_deposits[d_index].amount
	        d_index += 1
	        continue
	    except IndexError:
	      pass
	    current_date -= timedelta(days=1)
	  return (t_list, ver_balance)
	
	def GetPastBalances(self):
	  return self.account_balances.order('-paycheck.date')
	
	def GetAllBalancesAfterDate(self, date):
	  return self.account_balances.filter('date >=', date).fetch(100)
	
	def GetBalanceAdjustment(self, transaction):
	  if transaction.__class__.__name__ == 'Expense' or (transaction.__class__.__name__ == 'Transfer' and transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      amount = transaction.amount
	    else:
	      amount = transaction.amount * -1
	  else:
	    if self.a_type == 'Credit Card':
	      amount = transaction.amount * -1
	    else:
	      amount = transaction.amount
	  return amount
	
	def GetBalanceDifference(self, new_transaction, old_amount):
	  if new_transaction.__class__.__name__ == 'Expense' or (new_transaction.__class__.__name__ == 'Transfer' and new_transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      diff = new_transaction.amount - old_amount
	    else:
	      diff = old_amount - new_transaction.amount
	  else:
	    if self.a_type == 'Credit Card':
	      diff = old_amount - new_transaction.amount
	    else:
	      diff = new_transaction.amount - old_amount
	  return diff
	
	"""
	Adjusts verified account balance based on passed transaction amount to be
	verified (added/subtracted based on account and transaction types)
	"""
	def AdjustBalanceToVerifyTransaction(self, transaction, put=''):
	  if transaction.__class__.__name__ == 'Expense' or (transaction.__class__.__name__ == 'Transfer' and transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      self.ver_balance += transation.amount
	    else:
	      self.ver_balance -= transaction.amount
	  else:
	    if self.a_type == 'Credit Card':
	      self.ver_balance -= transaction.amount
	    else:
	      self.ver_balance += transaction.amount
	  if put == '': self.put()
	  return self
	
	"""
	Adjusts account balances based on passed removed transaction amount
	(added/subtracted based on account and transaction types)
	"""
	def AdjustBalanceToRemoveTransaction(self, transaction, put=''):
	  if transaction.__class__.__name__ == 'Expense' or (transaction.__class__.__name__ == 'Transfer' and transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      self.unv_balance -= transaction.amount
	      if transaction.verified:
	        self.ver_balance -= transation.amount
	    else:
	      self.unv_balance += transaction.amount
	      if transaction.verified:
	        self.ver_balance += transaction.amount
	  else:
	    if self.a_type == 'Credit Card':
	      self.unv_balance += transaction.amount
	      if transaction.verified:
	        self.ver_balance += transaction.amount
	    else:
	      self.unv_balance -= transaction.amount
	      if transaction.verified:
	        self.ver_balance -= transaction.amount
	  if put == '': self.put()
	  return self
	
	"""
	Adjusts account balances based on passed removed transaction amount
	(added/subtracted based on account and transaction types)
	"""
	def AdjustBalanceToAddTransaction(self, transaction, put=''):
	  if transaction.__class__.__name__ == 'Expense' or (transaction.__class__.__name__ == 'Transfer' and transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      self.unv_balance += transaction.amount
	      if transaction.verified:
	        self.ver_balance += transation.amount
	    else:
	      self.unv_balance -= transaction.amount
	      if transaction.verified:
	        self.ver_balance -= transaction.amount
	  else:
	    if self.a_type == 'Credit Card':
	      self.unv_balance -= transaction.amount
	      if transaction.verified:
	        self.ver_balance -= transaction.amount
	    else:
	      self.unv_balance += transaction.amount
	      if transaction.verified:
	        self.ver_balance += transaction.amount
	  if put == '': self.put()
	  return self
	
	def AdjustBalanceToEditTransactionAmount(self, transaction, edit_amount, put=''):
	  if transaction.__class__.__name__ == 'Expense' or (transaction.__class__.__name__ == 'Transfer' and transaction.receiving_account.key() != self.key()):
	    if self.a_type == 'Credit Card':
	      self.unv_balance += edit_amount
	      if transaction.verified:
	        self.ver_balance += edit_amount
	    else:
	      self.unv_balance -= edit_amount
	      if transaction.verified:
	        self.ver_balance -= edit_amount
	  else:
	    if self.a_type == 'Credit Card':
	      self.unv_balance -= edit_amount
	      if transaction.verified:
	        self.ver_balance -= edit_amount
	    else:
	      self.unv_balance += edit_amount
	      if transaction.verified:
	        self.ver_balance += edit_amount
	  if put == '': self.put()
	  return self

class Category(db.Model):
  id = db.StringProperty()
  name = db.StringProperty()
  type = db.StringProperty()
  has_subcats = db.BooleanProperty()
  subcats = db.ListProperty(db.Key)
  is_subcat = db.BooleanProperty()
  parent_cat = db.SelfReferenceProperty(collection_name='child_cats')
  
  """
  Category keyname format: "<name>-<parent/child>-cat"
  """
  @staticmethod
  def CreateKeyname(name, pc):
    key_name = name + '-'
    key_name += pc + '-'
    key_name += 'cat'
    return CleanKeyName(key_name)
  
  @staticmethod
  def CreateNewCategory(**kwargs):
    key_name = Category.CreateKeyname(kwargs['name'], kwargs['p/c'])
    cat = Category(key_name=key_name)
    cat.name = kwargs['name']
    cat.type = kwargs['type']
    if kwargs['p/c'] == 'child':
      cat.has_subcats = False
      cat.is_subcat = True
      cat.parent_cat = kwargs['parent'].key()
    else:
      cat.has_subcats = True
      cat.is_subcat = False
    return db.get(cat.put())
  
  @classmethod
  def GetAllParentCats(cls):
    return cls.all().filter('has_subcats = ', True).order('name')
  
  @classmethod
  def GetAllChildCats(cls):
    return cls.all().filter('has_subcats = ', False).order('name')
  
  @classmethod
  def GetChildCatGroupings(cls):
    cat_groups = []
    parents = cls.GetAllParentCats()
    for cat in parents:
      child_cat_list = cat.child_cats.order('name').fetch(100)
      if len(child_cat_list) != 0:
        cat_groups.append(child_cat_list)
    return cat_groups
  
  @staticmethod
  def GetExpensesFromCatInMonthBeforeDate(key_name, date):
    cat = Category.get_by_key_name(key_name)
    end_date = date - timedelta(days=30)
    if cat.has_subcats is True:
      results = cat.expenses_from_parent.filter('date <', date.isoformat())
    else:
      results = cat.expenses_from_child.filter('date <', date.isoformat())
    return results.filter('date >=', end_date.isoformat())

class Paycheck(db.Model):
	date = db.DateProperty()
	gross = db.FloatProperty()
	ret_401k = db.ReferenceProperty(collection_name='401k')
	after_deduction_balance = db.FloatProperty()
	after_transfer_balance = db.FloatProperty()
	final_balance = db.FloatProperty()
	current = db.BooleanProperty()
	closed = db.BooleanProperty()
	dest_account = db.ReferenceProperty(collection_name='dest_accounts')
	deposit_entity = db.ReferenceProperty(collection_name='p_deposits')
	
	"""
  Paycheck keyname format: yyyy-mm-dd-<ACCOUNTID>-<GROSSAMOUNT>
	"""
	@staticmethod
	def CreateKeyname(date, account, gross):
	  key_name = date + '-'
	  key_name += account + '-'
	  key_name += str(gross)
	  return CleanKeyName(key_name)
	
	@staticmethod
	def CreateNewPaycheck(**kwargs):
	  try:
	    key_name = Paycheck.CreateKeyname(kwargs['date'], kwargs['account'], kwargs['gross'])
	    new_paycheck = Paycheck(key_name=key_name)
	    new_paycheck.date = DateFromString(kwargs['date'])
	    new_paycheck.gross = float(kwargs['gross'])
	    new_paycheck.after_deduction_balance = new_paycheck.gross
	    new_paycheck.after_transfer_balance = new_paycheck.gross
	    new_paycheck.final_balance = new_paycheck.gross
	    account_key = Account.get_by_key_name(kwargs['account']).key()
	    new_paycheck.dest_account = account_key
	    if kwargs['current'] in ['True', True]:
	      new_paycheck.current = True
	    else:
	      new_paycheck.current = False
	    if kwargs['closed'] in ['True', True]:
	      new_paycheck.closed = True
	    else:
	      new_paycheck.closed = False
	    # put initial entity into DB
	    paycheck = db.get(new_paycheck.put())
	    # create deposit entity
	    deposit_args = {'date': kwargs['date'],
	                    'account_key_name': kwargs['account'],
	                    'account': account_key,
	                    'gross': kwargs['gross'],
	                    'after_deduction_balance': paycheck.after_deduction_balance,
	                    'paycheck': paycheck.key()}
	    deposit = Deposit.CreateNewPaycheckDeposit(**deposit_args)
	    # add deposit entity to paycheck
	    paycheck.deposit_entity = deposit.key()
	    # edit future PaycheckAccountBalance entities for paycheck account
	    PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToAddTransaction(paycheck.dest_account, paycheck.date, deposit)
	    # create PaycheckAccountBalance entities for other active accounts
	    active_accounts = Account.GetActiveAccountsAfterDate(kwargs['date'])
	    for a in active_accounts:
	      if a != paycheck.dest_account:
	        balance = a.CalculateBalanceAfterDate(kwargs['date'])
	        p = PaycheckAccountBalance.CreatePaycheckAccountBalance(a, paycheck, balance)
	    # put updated paycheck entity and return entity
	    return db.get(paycheck.put())
	  except KeyError as error:
	    logging.info('ERROR: ' + str(error))
	    return False
	
	def AddNewTax(self, **kwargs):
	  # create new tax entity
	  kwargs['paycheck_key'] = self.key()
	  t = Tax.CreateNewTax(**kwargs)
	  # adjust paycheck balances
	  self.after_deduction_balance -= t.amount
	  self.after_transfer_balance -= t.amount
	  self.final_balance -= t.amount
	  # adjust deposit entity amount and account balance
	  self.deposit_entity.EditPaycheckDepositAmount(t.amount * -1)
	  self.put()
	  return self
	
	def AddNewDeduction(self, **kwargs):
	  # create new deduction entity
	  kwargs['paycheck_key'] = self.key()
	  d = Deduction.CreateNewDeduction(**kwargs)
	  # adjust paycheck balances
	  self.after_deduction_balance -= d.amount
	  self.after_transfer_balance -= d.amount
	  self.final_balance -= d.amount
	  # adjust deposit entity amount and account balance
	  self.deposit_entity.EditPaycheckDepositAmount(d.amount * -1)
	  self.put()
	  return self
	
	def AddNewDeposit(self, **kwargs):
	  # create new deposit entity
	  kwargs['paycheck'] = self
	  kwargs['account'] = self.dest_account
	  d = Deposit.CreateNewDeposit(**kwargs)
	  # adjust paycheck balances
	  self.after_transfer_balance += d.amount
	  self.final_balance += d.amount
	  self.put()
	  return self
	
	def AddNewTransfer(self, **kwargs):
	  # create new transfer entity
	  kwargs['paycheck_key'] = self.key()
	  t = Transfer.CreateNewTransfer(**kwargs)
	  # adjust paycheck balances
	  self.after_transfer_balance -= t.amount
	  self.final_balance -= t.amount
	  self.put()
	  return self
	
	def AddNewExpense(self, **kwargs):
	  # create new expense entity
	  e = Expense.CreateNewExpense(**kwargs)
	  # adjust final paycheck balance
	  self.final_balance -= e.amount
	  self.put()
	  return self
	
	def AttachUnassignedExpense(self, expense):
	  if expense.__class__.__name__ is not 'Expense':
	    expense = Expense.get_by_key_name(expense)
	  expense.AttachToPaycheck(self)
	  self.final_balance -= expense.amount
	  self.put()
	  return self
	
	@classmethod
	def GetOpenPaychecks(cls):
	  return cls.all().filter('closed =', False).order('-date')
	
	def GetAllTaxes(self):
	  return self.paycheck_taxes
	
	def GetTaxTotal(self):
	  total = 0
	  taxes = self.paycheck_taxes.fetch(100)
	  for tax in taxes:
	    total += tax.amount
	  return total
	
	def GetFederalIncomeTax(self):
	  return self.paycheck_taxes.filter('tax_type =', 'Federal').get()
	
	def GetStateIncomeTax(self):
	  return self.paycheck_taxes.filter('tax_type =', 'State').get()
	
	def GetOtherTaxes(self):
	  q = self.paycheck_taxes.filter('tax_type !=', 'Federal')
	  return q.filter('tax_type !=', 'State').fetch(100)
	
	def GetAllDeductions(self):
	  return self.paycheck_deductions
	
	def GetDeductionsTotal(self):
	  total = 0
	  deductions = self.paycheck_deductions
	  for deduction in deductions:
	    total += deduction.amount
	  return total
	
	def GetMedicalDeduction(self):
	  return self.paycheck_deductions.filter('deduct_type =', 'Medical').get()
	
	def GetDentalDeduction(self):
	  return self.paycheck_deductions.filter('deduct_type =', 'Dental').get()
	
	def GetLifeDeduction(self):
	  return self.paycheck_deductions.filter('deduct_type =', 'Life').get()
	
	def GetVisionDeduction(self):
	  return self.paycheck_deductions.filter('deduct_type =', 'Vision').get()
	
	def GetOtherDeductions(self):
	  return self.paycheck_deductions.filter('deduct_type =', 'Other').fetch(100)
	
	def GetAllOtherDeposits(self):
	  return self.paycheck_deposits.filter('is_paycheck_deposit =', False).fetch(100)
	
	def GetOtherDepositsTotal(self):
	  total = 0
	  deposits = self.GetAllOtherDeposits()
	  for deposit in deposits:
	    total += deposit.amount
	  return total
	
	def GetAllTransfers(self):
	  return self.paycheck_transfers
	
	def GetTransfersTotal(self):
	  total = 0
	  transfers = self.GetAllTransfers()
	  for transfer in transfers:
	    total += transfer.amount
	  return total
	
	def GetAllDeposits(self):
	  return self.paycheck_deposits.filter('is_paycheck_deposit !=', True)
	
	def GetDepositsTotal(self):
	  total = 0
	  deposits = self.GetDepositsTotal()
	  for deposit in deposits:
	    total += deposit.amount
	  return total
	
	def GetAllExpenses(self):
	  return self.paycheck_expenses
	
	def GetExpensesTotal(self):
	  total = 0
	  for expense in self.GetAllExpenses():
	    total += expense.amount
	  return total
	
	def GetAllFoodExpenses(self):
	  expenses = self.GetAllExpenses()
	  food_parent_keyname = 'food-+-dining-parent-cat'
	  food_cat = Category.get_by_key_name(food_parent_keyname)
	  return expenses.filter('parent_e_category =', food_cat).fetch(100)
	
	def GetFoodExpensesTotal(self):
	  total = 0
	  for e in self.GetAllFoodExpenses():
	    total += e.amount
	  return total
	
	def GetAllMiscExpenses(self):
	  non_misc_parent_cats = ['food-+-dining-parent-cat']
	  non_misc_child_cats = []
	  q = self.GetAllExpenses()
	  for cat in non_misc_parent_cats:
	    c = Category.get_by_key_name(cat)
	    q = q.filter('parent_e_category !=', c)
	  for cat in non_misc_child_cats:
	    c = Category.get_by_key_name(cat)
	    q = q.filter('child_e_category !=', c)
	  return q.fetch(100)
	
	def GetMiscExpensesTotal(self):
	  total = 0
	  for e in self.GetAllMiscExpenses():
	    total += e.amount
	  return total
	
	def GetAccountBalances(self):
	  return PaycheckAccountBalance.GetPaycheckAccountBalances(self)
	
	def GetPreviousPaycheck(self): # still needs to be tested
	  return Paycheck.all().filter('date >', self.date).fetch(1)
	
	@classmethod
	def GetAllPaychecksAfterDate(cls, date):
	  return cls.all().filter('date >=', date).order('date').fetch(100)
	
	def RemoveTransaction(self, key_name):
	  # retrieve transaction from DB
	  transaction = Transaction.GetTransaction(key_name)
	  # edit paycheck balances and deposit entity amount (if transaction is tax or deduction)
	  if transaction.__class__.__name__ is 'Deposit':
	    self.final_balance -= transaction.amount
	  else:
	    self.final_balance += transaction.amount
	  if transaction.__class__.__name__ is not 'Expense':
	    if transaction.__class__.__name__ is 'Deposit':
	      self.after_transfer_balance -= transaction.amount
	    else:
	      self.after_transfer_balance += transaction.amount
	    if transaction.__class__.__name__ in ['Tax', 'Deduction']:
	      self.after_deduction_balance += transaction.amount
	      self.deposit_entity.EditPaycheckDepositAmount(transaction.amount)
	  # edit account balances (if transaction is not tax or deduction)
	  if transaction.__class__.__name__ not in ['Tax', 'Deduction']:
	    self.dest_account.AdjustBalanceToRemoveTransaction(transaction)
	    if transaction.__class__.__name__ is 'Transfer':
	      transaction.receiving_account.AdjustBalanceToRemoveTransaction(transaction)
	    # edit PaycheckAccountBalance entities
	    PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToRemoveTransaction(self.dest_account,
	                                                                                    transaction.date,
	                                                                                    transaction)
	    if transaction.__class__.__name__ is 'Transfer':
	      PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToRemoveTransaction(transaction.receiving_account,
	                                                                                      transaction.date,
	                                                                                      transaction)
	  # delete actual expense entity
	  db.delete(transaction.key())
	  self.put()
	  return self

class Transaction(db.Model):
	date = db.DateProperty()
	name = db.StringProperty()
	description = db.TextProperty()
	amount = db.FloatProperty()
	frequency = db.StringProperty(
	  choices = set(['Core', 'Regular', 'One-Time']),
	  default = 'One-Time')
	recurring_date = db.DateProperty()
	verified = db.BooleanProperty()
	
	@staticmethod
	def GetTransaction(key_name):
	  # retrieve transaction from DB
	  if Expense.get_by_key_name(key_name):
	    transaction = Expense.get_by_key_name(key_name)
	  elif Deduction.get_by_key_name(key_name):
	    transaction = Deduction.get_by_key_name(key_name)
	  elif Deposit.get_by_key_name(key_name):
	    transaction = Deposit.get_by_key_name(key_name)
	  elif Tax.get_by_key_name(key_name):
	    transaction = Tax.get_by_key_name(key_name)
	  elif Transfer.get_by_key_name(key_name):
	    transaction = Transfer.get_by_key_name(key_name)
	  return transaction
	
	@classmethod
	def GetAllTransactionsFromAccount(cls, account):
	  return cls.all().filter('account =', account).order('date').fetch(100)
	
	def GetClassName(self):
	  return self.__class__.__name__
	
	def GetNewAccountBalanceAfterRemoval(self, amount, account):
	  if self.GetClassName() == 'Expense' or (self.GetClassName() == 'Transfer' and self.receiving_account.key() != account.key()):
	    if account.a_type == 'Credit Card':
	      return_amount = amount - self.amount
	    else:
	      return_amount = amount + self.amount
	  else:
	    if account.a_type == 'Credit Card':
	      return_amount = amount + self.amount
	    else:
	      return_amount = amount - self.amount
	  return return_amount
	
	def Verify(self):
	  if self.verified != True:
	    if self.__class__.__name__ == 'Transfer':
	      self.origin_account.AdjustBalanceToVerifyTransaction(self)
	      self.receiving_account.AdjustBalanceToVerifyTransaction(self)
	    else:
	      self.account.AdjustBalanceToVerifyTransaction(self)
	    self.verified = True
	    self.put()
	  return self

class Expense(Transaction):
	paid = db.BooleanProperty()
	vendor = db.StringProperty()
	parent_e_category = db.ReferenceProperty(Category,
	                                         collection_name='expenses_from_parent')
	child_e_category = db.ReferenceProperty(Category,
	                                        collection_name='expenses_from_child')
	paycheck = db.ReferenceProperty(Paycheck,
	                                collection_name='paycheck_expenses')
	account = db.ReferenceProperty(Account,
	                               collection_name='account_expenses')
	
	"""
  Expense keyname formats:
    Expense - yyyy-mm-dd-<VENDOR>-<AMOUNT>-expense
	"""
	@staticmethod
	def CreateKeyname(date, vendor, amount):
	  key_name = date + '-'
	  key_name += vendor + '-'
	  key_name += str(amount) + '-'
	  key_name += 'expense'
	  return CleanKeyName(key_name)
	
	@staticmethod
	def CreateNewExpense(**kwargs):
	  key_name = Expense.CreateKeyname(kwargs['date'], kwargs['vendor'], kwargs['amount'])
	  expense = Expense(key_name=key_name)
	  expense.vendor = kwargs['vendor']
	  expense.date = DateFromString(str(kwargs['date']))
	  expense.description = kwargs['description']
	  expense.name = expense.description
	  expense.amount = float(kwargs['amount'])
	  expense.frequency = kwargs['frequency']
	  expense.verified = False
	  expense.paid = False
	  if kwargs['parent-cat'].__class__.__name__ is 'Category':
	    expense.parent_e_category = kwargs['parent-cat']
	  else:
	    expense.parent_e_category = Category.get_by_key_name(kwargs['parent-cat'])
	  if kwargs['child-cat'].__class__.__name__ is 'Category':
	    expense.child_e_category = kwargs['child-cat']
	  else:
	    expense.child_e_category = Category.get_by_key_name(kwargs['child-cat'])
	  if kwargs['account'].__class__.__name__ is 'Account':
	    expense.account = kwargs['account']
	  else:
	    expense.account = Account.get_by_key_name(kwargs['account'])
	  try:
	    expense.paycheck = kwargs['paycheck']
	  except KeyError:
	    expense.paycheck = None
	  # edit related account balance
	  expense.account.AdjustBalanceToAddTransaction(expense)
	  PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToAddTransaction(expense.account,
	                                                                               expense.date,
                                                                                 expense)
	  return db.get(expense.put())
	
	def AttachToPaycheck(self, paycheck, put=''):
	  self.paycheck = paycheck
	  if put == '': self.put()
	  return self
	
	@classmethod
	def GetUnassignedExpenses(cls):
	  return cls.all().filter('paycheck =', None).order('date')

class Tax(Transaction):
  tax_type = db.StringProperty(
    choices = set(['Federal', 'State', 'Disability', 'Medicare', 'Social Security', 'Other']))
  paycheck = db.ReferenceProperty(Paycheck,
                                  collection_name='paycheck_taxes')
  
  """
  CreateKeyname: Takes date and type of tax being created and creates standard format key name string
  Tax keyname format: "yyyy-mm-dd-<tax_type>(-name)(-income)-tax"
  Arguments:
    date (string) - Date of tax entity in ISO format (usually same as date of paycheck where tax is taken)
    tax_type (string) - Value for tax_type of Tax entity being created
    name (string) - Custom name of tax (if tax_type == 'Other')
  """
  @staticmethod
  def CreateKeyname(date, tax_type, name):
    key_name = date + '-'
    key_name += tax_type.lower() + '-'
    if tax_type.lower() in ['federal', 'state']:
      key_name += 'income' + '-'
    else:
      key_name += name.lower() + '-'
    key_name += 'tax'
    return CleanKeyName(key_name)

  @staticmethod
  def CreateNewTax(**kwargs):
    key_name = Tax.CreateKeyname(kwargs['date'], kwargs['tax-type'], kwargs['name'])
    tax = Tax(key_name=key_name)
    tax.date = DateFromString(str(kwargs['date']))
    tax.tax_type = kwargs['tax-type']
    if kwargs['tax-type'] in ['Federal', 'State']:
      tax.name = kwargs['tax-type'] + ' Income Tax'
    else:
      tax.name = kwargs['name']
    tax.description = tax.name
    tax.amount = float(kwargs['amount'])
    tax.frequency = 'Core'
    tax.verified = True
    tax.paycheck = db.get(kwargs['paycheck_key'])
    return db.get(tax.put())

class Deduction(Transaction):
  deduct_type = db.StringProperty(
    choices = set(['Medical', 'Dental', 'Vision', 'Life', 'Gym', 'Internet', 'Other']))
  paycheck = db.ReferenceProperty(Paycheck,
                                  collection_name='paycheck_deductions')

  """
  CreateKeyname: Takes date and type of tax being created and creates standard format key name string
  Deduction keyname format: "yyyy-mm-dd-<deduct_type>(-name)-deduction"
  Arguments:
    date (string) - Date of deduction entity in ISO format (usually same as date of paycheck where deduction occured)
    deduct_type (string) - Value for deduct_type of Deduction entity being created
    name (string) - Custom name of deduction (if deduct_type == 'Other')
  """
  @staticmethod
  def CreateKeyname(date, deduct_type, name):
    key_name = date + '-'
    key_name += deduct_type.lower() + '-'
    type_choices = ['medical', 'dental', 'vision', 'life', 'gym', 'internet']
    if deduct_type.lower() not in type_choices:
      key_name += name.lower() + '-'
    key_name += '-deduction'
    return CleanKeyName(key_name)

  @staticmethod
  def CreateNewDeduction(**kwargs):
    key_name = Deduction.CreateKeyname(kwargs['date'], kwargs['deduct-type'], kwargs['name'])
    d = Deduction(key_name=key_name)
    d.date = DateFromString(str(kwargs['date']))
    d.deduct_type = kwargs['deduct-type']
    if kwargs['deduct-type'] in ['Medical', 'Dental', 'Vision', 'Life']:
      d.name = kwargs['deduct-type'] + ' Insurance Deduction'
    elif kwargs['deduct-type'] in ['Gym']:
      d.name = kwargs['deduct-type'] + ' Deduction'
    elif kwargs['deduct-type'] is 'Internet':
      d.name = kwargs['deduct-type'] + ' Reimbursement Deduction'
    else:
      d.name = kwargs['name']
    d.description = d.name
    d.amount = float(kwargs['amount'])
    d.frequency = 'Core'
    d.verified = True
    d.paycheck = db.get(kwargs['paycheck_key'])
    return db.get(d.put())

class Deposit(Transaction):
	source = db.StringProperty()
	d_type = db.StringProperty(
	  choices = set(['Paycheck', 'Other']),
	  default = 'Savings')
	is_paycheck_deposit = db.BooleanProperty()
	paycheck = db.ReferenceProperty(Paycheck,
	                                collection_name='paycheck_deposits')
	account = db.ReferenceProperty(Account,
	                               collection_name='account_deposits')
	
	"""
	Deposit keyname formats:
	  Initial Paycheck Deposit - yyyy-mm-dd-<ACCOUNTID>-<GROSSAMOUNT>-paycheckdeposit
	  Deposit - yyyy-mm-dd-<SOURCE>-<AMOUNT>-deposit
	"""
	@staticmethod
	def CreateKeyname(d_date, type, **kwargs):
	  key_name = d_date + '-'
	  if type == 'paycheckdeposit':
	    key_name += kwargs['account'] + '-'
	    key_name += kwargs['gross'] + '-'
	  elif type == 'deposit':
	    key_name += kwargs['source'] + '-'
	    key_name += kwargs['amount'] + '-'
	  key_name += type
	  return CleanKeyName(key_name)
	
	@staticmethod
	def CreateNewPaycheckDeposit(**kwargs):
	  try:
	    # create new deposit entity
	    keyname_args = {'account': kwargs['account_key_name'],
	                    'gross': kwargs['gross']}
	    key_name = Deposit.CreateKeyname(kwargs['date'], 'paycheckdeposit', **keyname_args)
	    new_deposit = Deposit(key_name=key_name, d_type='Paycheck')
	    new_deposit.date = DateFromString(kwargs['date'])
	    new_deposit.amount = kwargs['after_deduction_balance']
	    new_deposit.description = 'General after-deduction deposit for '
	    new_deposit.description += str(new_deposit.date) + ' paycheck'
	    new_deposit.account = kwargs['account']
	    new_deposit.source = 'Paycheck'
	    new_deposit.is_paycheck_deposit = True
	    new_deposit.paycheck = kwargs['paycheck']
	    new_deposit.frequency = 'Core'
	    new_deposit.name = str(new_deposit.date) + ' Paycheck Deposit - '
	    new_deposit.name += new_deposit.account.name
	    new_deposit.verified = True
	    deposit = db.get(new_deposit.put())
	    # update account unverified balance
	    deposit.account.AdjustBalanceToAddTransaction(deposit)
	    return deposit
	  except KeyError as error:
	    logging.info('ERROR: ' + str(error))
	    return False
	
	@staticmethod
	def CreateNewDeposit(**kwargs):
	  try:
	    # create new deposit entity
	    key_name = Deposit.CreateKeyname(kwargs['date'], 'deposit', **kwargs)
	    new_deposit = Deposit(key_name=key_name, d_type='Other')
	    new_deposit.date = DateFromString(kwargs['date'])
	    new_deposit.amount = float(kwargs['amount'])
	    new_deposit.source = kwargs['source']
	    new_deposit.description = kwargs['description']
	    new_deposit.name = 'Deposit from ' + new_deposit.source
	    new_deposit.account = kwargs['account']
	    new_deposit.d_type = 'Other'
	    new_deposit.is_paycheck_deposit = False
	    new_deposit.paycheck = kwargs['paycheck']
	    new_deposit.frequency = 'One-Time'
	    new_deposit.verified = False
	    deposit = db.get(new_deposit.put())
	    # update account unverified balance and all PaycheckAccountBalance entities after deposit date
	    deposit.account.AdjustBalanceToAddTransaction(deposit)
	    PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToAddTransaction(deposit.account,
  	                                                                               deposit.date,
  	                                                                               deposit)
	    return deposit
	  except KeyError as error:
	    logging.info('ERROR: ' + str(error))
	    return False
	
	def EditPaycheckDepositAmount(self, amount):
	  old_amount = self.amount
	  self.amount += amount
	  self.put()
	  self.account.AdjustBalanceToEditTransactionAmount(self, amount)
	  PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToEditTransaction(self.account,
	                                                                                self.date,
	                                                                                self,
	                                                                                old_amount)
	  return self

class Transfer(Transaction):
  origin_account = db.ReferenceProperty(Account,
                                        collection_name='transfers_origin')
  receiving_account = db.ReferenceProperty(Account,
                                            collection_name='transfers_receiving')
  paycheck = db.ReferenceProperty(Paycheck,
                                  collection_name='paycheck_transfers')
  
  """
  CreateKeyname: Takes date and accounts of transfer being created and creates standard format key name string
  Transfer keyname format: "yyyy-mm-dd-<origin_account>-<rec_account>-amount-transfer"
  Arguments:
    date (string) - Date of deduction entity in ISO format (usually same as date of paycheck where transer is associated)
    origin_account (string) - Name of transfer origin account
    rec_account (string) - Name of transfer destination account
    amount (float or string) - Amount of transfer
  """
  @staticmethod
  def CreateKeyname(date, origin_account, rec_account, amount):
    key_name = date + '-'
    key_name += origin_account.lower() + '-'
    key_name += rec_account.lower() + '-'
    key_name += str(amount) + '-'
    key_name += '-transfer'
    return CleanKeyName(key_name)
  
  @staticmethod
  def CreateNewTransfer(**kwargs):
    key_name = Transfer.CreateKeyname(kwargs['date'], kwargs['origin-account'].name,
                                      kwargs['rec-account'].name, kwargs['amount'])
    t = Transfer(key_name=key_name)
    t.date = DateFromString(str(kwargs['date']))
    t.description = kwargs['description']
    t.name = t.description
    t.amount = float(kwargs['amount'])
    t.frequency = 'One-Time'
    t.verified = False
    t.origin_account = kwargs['origin-account']
    t.receiving_account = kwargs['rec-account']
    t.paycheck = db.get(kwargs['paycheck_key'])
    transfer = db.get(t.put())
    # adjust account balances
    transfer.origin_account.AdjustBalanceToAddTransaction(transfer)
    transfer.receiving_account.AdjustBalanceToAddTransaction(transfer)
    PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToAddTransaction(transfer.origin_account,
                                                                                 transfer.paycheck.date,
                                                                                 transfer)
    PaycheckAccountBalance.AdjustAllBalancesFromAccountAfterDateToAddTransaction(transfer.receiving_account,
                                                                                 transfer.paycheck.date,
                                                                                 transfer)
    return transfer

# TODO: Decide how to handle unv vs. ver balances
class PaycheckAccountBalance(db.Model):
  balance = db.FloatProperty(required=True)
  date = db.DateProperty(required=True)
  account = db.ReferenceProperty(Account,
                                 required=True,
                                 collection_name='account_balances')
  paycheck = db.ReferenceProperty(Paycheck,
                                  required=True,
                                  collection_name='paycheck_balances')
  
  @staticmethod
  def CreateKeyname(account_name, date):
    key_name = account_name + '-'
    key_name += date.isoformat() + '-'
    key_name += 'balance'
    return key_name
  
  @staticmethod
  def CreatePaycheckAccountBalance(account, paycheck, balance):
    key_name = PaycheckAccountBalance.CreateKeyname(account.name, paycheck.date)
    balance = PaycheckAccountBalance(key_name=key_name,
                                     balance=balance,
                                     date=paycheck.date,
                                     paycheck=paycheck,
                                     account=account)
    balance.put()
    return balance
  
  @classmethod
  def GetAllBalancesFromAccountAfterDate(cls, account, date):
    return cls.all().filter('account =', account).filter('date >=', date).fetch(100)
  
  @classmethod
  def GetPaycheckAccountBalances(cls, paycheck):
    return cls.all().filter('paycheck =', paycheck).order('account').fetch(50)
  
  @classmethod
  def AdjustAllBalancesFromAccountAfterDateToEditTransaction(cls, account, date, transaction, old_amount=0):
    logging.info('Enter editing!!!!')
    balances = cls.GetAllBalancesFromAccountAfterDate(account, date)
    try:
      for b in balances:
        b.balance += b.account.GetBalanceDifference(transaction, old_amount)
        b.put()
      return True
    except IndexError:
      return False
  
  @classmethod
  def AdjustAllBalancesFromAccountAfterDateToRemoveTransaction(cls, account, date, transaction):
    balances = cls.GetAllBalancesFromAccountAfterDate(account, date)
    try:
      for b in balances:
        b.balance -= b.account.GetBalanceAdjustment(transaction)
        b.put()
      return True
    except IndexError:
      return False
  
  @classmethod
  def AdjustAllBalancesFromAccountAfterDateToAddTransaction(cls, account, date, transaction):
    balances = cls.GetAllBalancesFromAccountAfterDate(account, date)
    try:
      for b in balances:
        b.balance += b.account.GetBalanceAdjustment(transaction)
        b.put()
      return True
    except IndexError:
      return False

def DateFromString(string_date):
  new_date = datetime.strptime(string_date, '%Y-%m-%d')
  return date(new_date.year, new_date.month, new_date.day)

def CleanKeyName(key_name):
  key_name = key_name.replace(' ', '-').replace('&', '+').replace('--', '-')
  key_name = key_name.replace('--', '-').lower()
  return key_name