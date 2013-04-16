#usr/bin/python2.7

import db as mydb
import unittest

from datetime import date
from google.appengine.ext import db
from google.appengine.ext import testbed

class DbTest(unittest.TestCase):
  
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
  
  def tearDown(self):
    self.testbed.deactivate()
  
  def addAccountStub(self, name = 'New Account',
                     type = 'Checking',
                     starting = float(1000),
                     date = '2012-01-01',
                     verified = '2012-01-01'):
    account_args = {'name': name,
                    'type': type,
                    'starting': starting,
                    'start-date': date,
                    'last-verified': verified}
    return (mydb.Account.CreateNewAccount(**account_args), account_args)
  
  def initializeAccountsStub(self):
    self.addAccountStub(name = 'Checking Account')
    self.addAccountStub(name = 'Savings Account', type = 'Savings')
    self.addAccountStub(name = 'Investment Account', type = 'Investment')
    self.addAccountStub(name = 'Credit Card Account', type = 'Credit Card')
    return 4 # return number of accounts created
  
  def addExpenseStub(self, account,
                     date = '2012-01-01',
                     amount = '100',
                     vendor = 'Test Vendor',
                     description = 'Test Description',
                     frequency = 'One-Time',
                     paycheck_key_name = None,
                     pcat = None,
                     ccat = None,
                     verified = False):
    expense_args = {'date': date,
                    'amount': amount,
                    'vendor': vendor,
                    'description': description,
                    'account': account,
                    'frequency': frequency,
                    'paycheck': paycheck_key_name,
                    'parent-cat': pcat,
                    'child-cat': ccat,
                    'verified': verified}
    return (mydb.Expense.CreateNewExpense(**expense_args), expense_args)

  def addDepositStub(self, account,
                     date = '2012-01-01',
                     amount = '100',
                     source = 'Test Source',
                     description = 'Test Description',
                     verified = False):
    deposit_args = {'date': date,
                    'amount': amount,
                    'source': source,
                    'description': description,
                    'account': account,
                    'paycheck': None,
                    'verified': verified}
    return (mydb.Deposit.CreateNewDeposit(**deposit_args), deposit_args)
  
  def addTransferStub(self, account, rec_account,
                      date = '2012-01-01',
                      amount = '100',
                      description = 'Test Description',
                      verified = False):
    transfer_args = {'date': date,
                     'amount': amount,
                     'origin-account': account,
                     'rec-account': rec_account,
                     'description': description,
                     'verified': verified}
    return (mydb.Transfer.CreateNewTransfer(**transfer_args), transfer_args)

if __name__ == '__main__':
  unittest.main()