#usr/bin/python2.7

import db as mydb
import db_test_stubs as stubs
import unittest

from datetime import date
from google.appengine.ext import db
from google.appengine.ext import testbed

class DbAccountTest(stubs.DbTest):

  def testAccountCreateKeyname(self):
    keyname = mydb.Account.CreateKeyname('name', 'type')
    # correct format
    self.assertEqual('name-type-account', keyname)
    # 3 sections separated by -
    self.assertEqual(3, len(keyname.split('-')))
  
  def testAccountCreateNewAccount(self):
    a_tuple = self.addAccountStub()
    a = a_tuple[0]
    a_args = a_tuple[1]
    # a is Account object
    self.assertIsInstance(a, mydb.Account)
    # Account created with correct data
    self.assertEqual(a.name, a_args['name'])
    self.assertEqual(a.a_type, a_args['type'])
    self.assertEqual(a.unv_balance, a_args['starting'])
    self.assertEqual(a.start_date.year, int(a_args['start-date'].split('-')[0]))
    self.assertEqual(a.start_date.month, int(a_args['start-date'].split('-')[1]))
    self.assertEqual(a.start_date.day, int(a_args['start-date'].split('-')[2]))
    self.assertEqual(a.last_verified.year, int(a_args['last-verified'].split('-')[0]))
    self.assertEqual(a.last_verified.month, int(a_args['last-verified'].split('-')[1]))
    self.assertEqual(a.last_verified.day, int(a_args['last-verified'].split('-')[2]))
    # Verified and unverified balances of new account are the same
    self.assertEqual(a.unv_balance, a.ver_balance)
  
  def testGetAllAccounts(self):
    # returns empty query if no accounts
    a = mydb.Account.GetAllAccounts()
    self.assertEqual(a.count(), 0)
    # returns all accounts
    num_accounts = self.initializeAccountsStub()
    a = mydb.Account.GetAllAccounts()
    self.assertEqual(num_accounts, a.count())
  
  def testGetAllPaymentAccounts(self):
    # returns empty query if no accounts
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 0)
    # counts Checking accounts as payment accounts
    self.addAccountStub(type = 'Checking')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'C Account 2', type = 'Checking')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 2)
    # also counts Credit Card accounts as payment accounts
    self.addAccountStub(name = 'CC Account 1', type = 'Credit Card')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 3)
    self.addAccountStub(name = 'CC Account 2', type = 'Credit Card')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 4)
    # returns 0 if no Checking or Credit Card Accounts
    for account in a: db.delete(account.key())
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 0)
    # counts Credit Card accounts as payment accounts (without also having Checking accounts)
    self.addAccountStub(name = 'CC Account 1', type = 'Credit Card')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'CC Account 2', type = 'Credit Card')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 2)
    # doesn't count Investment or Savings accounts
    self.addAccountStub(type = 'Investment')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 2)
    self.addAccountStub(type = 'Savings')
    a = mydb.Account.GetAllPaymentAccounts()
    self.assertEqual(a.count(), 2)
  
  def testGetAllNonCheckingAccounts(self):
    # returns empty query if no accounts
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 0)
    # counts only Savings accounts
    self.addAccountStub(type = 'Savings')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'S Account 2', type = 'Savings')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 2)
    for account in a: db.delete(account.key())
    # counts only Investment accounts
    self.addAccountStub(type = 'Investment')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'I Account 2', type = 'Investment')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 2)
    for account in a: db.delete(account.key())
    # counts only Credit Card accounts
    self.addAccountStub(type = 'Credit Card')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'CC Account 2', type = 'Credit Card')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 2)
    for account in a: db.delete(account.key())
    # doesn't count Checking accounts
    self.addAccountStub(type = 'Checking')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 0)
    self.addAccountStub(name = 'C Account 2', type = 'Checking')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 0)
    for account in a: db.delete(account.key())
    # counts Savings, Investment, Credit Card accounts together
    self.addAccountStub(type = 'Savings')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'I Account', type = 'Investment')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 2)
    self.addAccountStub(name = 'CC Account', type = 'Credit Card')
    a = mydb.Account.GetAllNonCheckingAccounts()
    self.assertEqual(a.count(), 3)
  
  def testGetAllCheckingSavingsAccounts(self):
    # returns empty query if no accounts
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 0)
    # counts only Checking accounts
    self.addAccountStub(type = 'Checking')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'C Account 2', type = 'Checking')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 2)
    for account in a: db.delete(account.key())
    # counts only Savings accounts
    self.addAccountStub(type = 'Savings')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'S Account 2', type = 'Savings')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 2)
    for account in a: db.delete(account.key())
    # counts both Checking and Savings accounts
    self.addAccountStub(type = 'Checking')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'S Account', type = 'Savings')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 2)
    # doesn't count Investment or Credit Card accounts
    self.addAccountStub(name = 'I Account', type = 'Investment')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 2)
    self.addAccountStub(name = 'CC Account', type = 'Credit Card')
    a = mydb.Account.GetAllCheckingSavingsAccounts()
    self.assertEqual(a.count(), 2)
  
  def testGetAllCreditCardAccounts(self):
    # returns empty query if no accounts
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 0)
    # returns Credit Card accounts
    self.addAccountStub(type = 'Credit Card')
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'CC Account 2', type = 'Credit Card')
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 2)
    # doesn't return Checking, Investment or Savings accounts
    self.addAccountStub(name = 'I Account', type = 'Investment')
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 2)
    self.addAccountStub(name = 'C Account', type = 'Checking')
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 2)
    self.addAccountStub(name = 'S Account', type = 'Savings')
    a = mydb.Account.GetAllCreditCardAccounts()
    self.assertEqual(a.count(), 2)
  
  def testAccountGetActiveAccountsAfterDate(self):
    # returns None if start_date not date text
    start_date = '5'
    self.assertEqual(None, mydb.Account.GetActiveAccountsAfterDate(start_date))
    # returns empty query if no accounts
    a = mydb.Account.GetActiveAccountsAfterDate('2012-01-01')
    self.assertEqual(a.count(), 0)
    # returns accounts with start_date after specified date
    self.addAccountStub(date = '2012-01-02')
    a = mydb.Account.GetActiveAccountsAfterDate('2012-01-01')
    self.assertEqual(a.count(), 1)
    self.addAccountStub(name = 'Account 2', date = '2013-01-01')
    a = mydb.Account.GetActiveAccountsAfterDate('2012-01-01')
    self.assertEqual(a.count(), 2)
    # doesn't return accounts with start_date before specified date
    self.addAccountStub(name = 'Account 3', date = '2011-12-31')
    a = mydb.Account.GetActiveAccountsAfterDate('2012-01-01')
    self.assertEqual(a.count(), 2)
    self.addAccountStub(name = 'Account 4', date = '2011-01-01')
    a = mydb.Account.GetActiveAccountsAfterDate('2012-01-01')
    self.assertEqual(a.count(), 2)
  
  def testGetTotalUnvBalanceFromAllAccounts(self):
    # returns 0 if no accounts
    self.assertEqual(mydb.Account.GetTotalUnvBalanceFromAllAccounts(), 0)
    # returns correct balance from one account
    self.addAccountStub()
    self.assertEqual(mydb.Account.GetTotalUnvBalanceFromAllAccounts(), 1000)
    # returns correct total from multiple accounts
    self.addAccountStub(name = 'Account 2', starting = float(100))
    self.assertEqual(mydb.Account.GetTotalUnvBalanceFromAllAccounts(), 1100)
    self.addAccountStub(name = 'Account 3', starting = float(500))
    self.assertEqual(mydb.Account.GetTotalUnvBalanceFromAllAccounts(), 1600)
  
  def testGetAllExpensesFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no expenses
    self.assertEqual(a.GetAllExpensesFromAccount().count(), 0)
    # returns proper number of expenses
    self.addExpenseStub(a)
    self.assertEqual(a.GetAllExpensesFromAccount().count(), 1)
    self.addExpenseStub(a, date='2013-01-01')
    self.assertEqual(a.GetAllExpensesFromAccount().count(), 2)
  
  def testGetAllUnverifiedExpensesFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no expenses
    self.assertEqual(a.GetAllUnverifiedExpensesFromAccount().count(), 0)
    # returns empty query if only verified expenses
    self.addExpenseStub(a, verified = True)
    self.assertEqual(a.GetAllUnverifiedExpensesFromAccount().count(), 0)
    # returns proper number of unverified expenses
    self.addExpenseStub(a, date = '2012-04-01')
    self.assertEqual(a.GetAllUnverifiedExpensesFromAccount().count(), 1)
    self.addExpenseStub(a, date = '2012-07-01')
    self.assertEqual(a.GetAllUnverifiedExpensesFromAccount().count(), 2)
  
  def testGetAllVerifiedExpensesFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no expenses
    self.assertEqual(a.GetAllVerifiedExpensesFromAccount().count(), 0)
    # returns empty query if only unverified expenses
    self.addExpenseStub(a)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccount().count(), 0)
    # returns proper number of verified expenses
    self.addExpenseStub(a, date = '2012-04-01', verified = True)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccount().count(), 1)
    self.addExpenseStub(a, date = '2012-07-01', verified = True)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccount().count(), 2)
  
  def testGetAllVerifiedExpensesFromAccountAfterDate(self):
    a = self.addAccountStub()[0]
    # returns empty query if no expenses
    self.assertEqual(a.GetAllVerifiedExpensesFromAccountAfterDate('2012-01-01').count(), 0)
    # returns empty query if only unverified expenses
    self.addExpenseStub(a, verified = False)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccountAfterDate('2012-01-01').count(), 0)
    # returns empty query if only verified expenses before specified date
    self.addExpenseStub(a, date = '2011-01-01', verified = True)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccountAfterDate('2012-01-01').count(), 0)
    # returns proper number of verified expenses after specified date
    self.addExpenseStub(a, date = '2012-01-02', verified = True)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccountAfterDate('2012-01-01').count(), 1)
    self.addExpenseStub(a, date = '2013-01-01', verified = True)
    self.assertEqual(a.GetAllVerifiedExpensesFromAccountAfterDate('2012-01-01').count(), 2)
  
  def testGetAllDepositsFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no deposits
    self.assertEqual(a.GetAllDepositsFromAccount().count(), 0)
    # returns proper number of deposits
    self.addDepositStub(a)
    self.assertEqual(a.GetAllDepositsFromAccount().count(), 1)
    self.addDepositStub(a, date='2013-01-01')
    self.assertEqual(a.GetAllDepositsFromAccount().count(), 2)
  
  def testGetAllUnverifiedDepositsFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no deposits
    self.assertEqual(a.GetAllUnverifiedDepositsFromAccount().count(), 0)
    # returns empty query if only verified deposits
    self.addDepositStub(a, verified = True)
    self.assertEqual(a.GetAllUnverifiedDepositsFromAccount().count(), 0)
    # returns proper number of unverified deposits
    self.addDepositStub(a, date = '2012-04-01')
    self.assertEqual(a.GetAllUnverifiedDepositsFromAccount().count(), 1)
    self.addDepositStub(a, date = '2012-07-01')
    self.assertEqual(a.GetAllUnverifiedDepositsFromAccount().count(), 2)
  
  def testGetAllVerifiedDepositsFromAccount(self):
    a = self.addAccountStub()[0]
    # returns empty query if no deposits
    self.assertEqual(a.GetAllVerifiedDepositsFromAccount().count(), 0)
    # returns empty query if only unverified deposits
    self.addDepositStub(a)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccount().count(), 0)
    # returns proper number of verified deposits
    self.addDepositStub(a, date = '2012-04-01', verified = True)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccount().count(), 1)
    self.addDepositStub(a, date = '2012-07-01', verified = True)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccount().count(), 2)
  
  def testGetAllVerifiedDepositsFromAccountAfterDate(self):
    a = self.addAccountStub()[0]
    # returns empty query if no expenses
    self.assertEqual(a.GetAllVerifiedDepositsFromAccountAfterDate('2012-01-01').count(), 0)
    # returns empty query if only unverified deposits
    self.addDepositStub(a, verified = False)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccountAfterDate('2012-01-01').count(), 0)
    # returns empty query if only verified deposits before specified date
    self.addDepositStub(a, date = '2011-01-01', verified = True)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccountAfterDate('2012-01-01').count(), 0)
    # returns proper number of verified deposits after specified date
    self.addDepositStub(a, date = '2012-01-02', verified = True)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccountAfterDate('2012-01-01').count(), 1)
    self.addDepositStub(a, date = '2013-01-01', verified = True)
    self.assertEqual(a.GetAllVerifiedDepositsFromAccountAfterDate('2012-01-01').count(), 2)
  
  def testCalculateBalanceAfterDate(self):
    a = self.addAccountStub()[0]
    rec_a = self.addAccountStub(type = 'Savings')[0]
    # returns current verified balance if no transactions
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1000)
    # returns same balance for static date if transactions added after
    self.addExpenseStub(a, date = '2012-04-01', amount = '200', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1000)
    self.addDepositStub(a, date = '2012-04-01', amount = '200', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1000)
    self.addTransferStub(a, rec_a, date = '2012-04-01', amount = '200', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1000)
    # returns new balance based on transactions before date
    self.addExpenseStub(a, date = '2011-03-01', amount = '50', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 950)
    self.addDepositStub(a, date = '2011-04-01', amount = '100', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1050)
    self.addTransferStub(a, rec_a, date = '2011-05-01', amount = '25', verified = True)
    self.assertEqual(a.CalculateBalanceAfterDate('2012-01-01'), 1025)
  
  def testRecentUnvTransactionBalanceList(self):
    a = self.addAccountStub(starting = float(500))[0]
    rec_a = self.addAccountStub(type = 'Savings')[0]
    # returns tuple with empty list and unchanged balance if no transactions
    test_v = a.GetRecentUnvTransactionBalanceList()
    self.assertEqual(len(test_v[0]), 0)
    self.assertEqual(test_v[1], 500)
    # counts expenses and appropriately changes balance
    self.addExpenseStub(a, date = '2012-01-01', amount = '100', vendor = 'Testy', verified = False)
    test_v = a.GetRecentUnvTransactionBalanceList()
    self.assertEqual(len(test_v[0]), 1)
    self.assertEqual(test_v[0][0][0].vendor, 'Testy')
    self.assertEqual(test_v[0][0][1], 400)
    self.assertEqual(test_v[1], 500)
    self.addExpenseStub(a, date = '2012-01-02', amount = '50', vendor = 'Testy 2', verified = False)
    test_v = a.GetRecentUnvTransactionBalanceList()
    self.assertEqual(len(test_v[0]), 2)
    self.assertEqual(test_v[0][0][0].vendor, 'Testy 2')
    self.assertEqual(test_v[0][0][1], 350)
    self.assertEqual(test_v[0][1][0].vendor, 'Testy')
    self.assertEqual(test_v[0][1][1], 400)
    self.assertEqual(test_v[1], 500)
    # counts deposits and appropriately changes balance
    self.addDepositStub(a, date = '2012-01-03', amount = '25', source = 'Testy 3', verified = False)
    test_v = a.GetRecentUnvTransactionBalanceList()
    self.assertEqual(len(test_v[0]), 3)
    self.assertEqual(test_v[0][0][0].source, 'Testy 3')
    self.assertEqual(test_v[0][0][1], 375)
    self.assertEqual(test_v[0][2][0].vendor, 'Testy')
    self.assertEqual(test_v[0][2][1], 400)
    self.assertEqual(test_v[1], 500)
    # counts transfers and appropriately changes balance
    self.addTransferStub(a, rec_a, date = '2012-01-04', description = 'Test Descripty 1',
                        amount = '100', verified = False)
    test_v = a.GetRecentUnvTransactionBalanceList()
    self.assertEqual(len(test_v[0]), 4)
    self.assertEqual(test_v[0][0][0].description, 'Test Descripty 1')
    self.assertEqual(test_v[0][0][1], 275)
    self.assertEqual(test_v[0][2][0].vendor, 'Testy 2')
    self.assertEqual(test_v[0][2][1], 350)
    self.assertEqual(test_v[0][3][0].vendor, 'Testy')
    self.assertEqual(test_v[0][3][1], 400)
    self.assertEqual(test_v[1], 500)
  
  def testDateFromString(self):
    good_string_date = '2012-04-01'
    # string_date not date text
    bad_string_date = '5'
    self.assertEqual(None, mydb.DateFromString(bad_string_date))
    # returns date object
    self.assertIsInstance(mydb.DateFromString(good_string_date), date)
    # returns correct date
    self.assertEqual(mydb.DateFromString(good_string_date).year, int(good_string_date.split('-')[0]))
    self.assertEqual(mydb.DateFromString(good_string_date).month, int(good_string_date.split('-')[1]))
    self.assertEqual(mydb.DateFromString(good_string_date).day, int(good_string_date.split('-')[2]))

if __name__ == '__main__':
  unittest.main()