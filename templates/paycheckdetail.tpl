{% extends "base.tpl" %}

{% block main %}
<h2>{{ paycheck.date}} Paycheck</h2>
<p><strong>GROSS</strong>: ${{ paycheck.gross|floatformat:"2" }}</p>
<p>Taxes:</p>
<ul>
  {% if taxes %}
  {% for tax in taxes %}
	<li>{{ tax.name }}: ${{ tax.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li>No taxes entered</li>
	{% endif %}
</ul>
<p><strong>Total taxes:</strong> ${{ tax_total|floatformat:"2" }}</p>
<form>
  Name: <input type="text" name="tax-name"><br />
  Description: <input type="text" name="tax-description"><br />
  Amount: <input type="text" name="tax-amount">
<p>Deductions:</p>
<ul>
  {% if deductions %}
  {% for d in deductions %}
	<li>{{ d.name }}: ${{ d.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li>No deductions entered</li>
	{% endif %}
</ul>
<p><strong>Total deductions:</strong> ${{ deductions_total|floatformat:"2" }}</p>
  Name: <input type="text" name="deduction-name"><br />
  Description: <input type="text" name="deduction-description"><br />
  Amount: <input type="text" name="deduction-amount"><br />
  Category: <input type="text" name="deduction-category">
<p><strong>AFTER DEDUCTIONS</strong>: ${{ paycheck.after_deduction_balance|floatformat:"2" }}</p>
<p>Deposits:</p>
<ul>
  {% if deposits %}
  {% for d in deposits %}
	<li>{{ d.name }}: ${{ d.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li>No deposits entered</li>
	{% endif %}
</ul>
<p><strong>Total deposits:</strong> ${{ deposits_total|floatformat:"2" }}</p>
  Name: <input type="text" name="deposit-name"><br />
  Description: <input type="text" name="deposit-description"><br />
  Amount: <input type="text" name="deposit-amount"><br />
  Category: <input type="text" name="deposit-category">
<p><strong>AFTER DEPOSITS</strong>: ${{ paycheck.after_deposit_balance|floatformat:"2" }}</p>
<p>Expenses:</p>
<ul>
  {% if expenses %}
  {% for expense in expenses %}
	<li>{{ expense.name }}: ${{ expense.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li>No expenses entered</li>
	{% endif %}
</ul>
<p><strong>Total expenses:</strong> ${{ expenses_total|floatformat:"2" }}</p>
  Name: <input type="text" name="expense-name"><br />
  Description: <input type="text" name="expense-description"><br />
  Amount: <input type="text" name="expense-amount"><br />
  Category: <input type="text" name="expense-category">
<p><strong>FINAL PAYCHECK BALANCE</strong>: ${{ paycheck.final_balance|floatformat:"2" }}</p>
<br />
<input type="submit" value="Submit">
</form>
{% endblock main %}