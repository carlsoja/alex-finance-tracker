{% extends "base.tpl" %}

{% block main %}
<h2>Unassigned expenses</h2>
<form action="" method="post">
{% for expense in expenses %}
<input type="checkbox" name="expense" value="{{ expense.key }}">{{ expense.date }}: {{ expense.name }}<br />
${{ expense.amount }}, {{ expense.frequency }}</input>
<br />
{% endfor %}
<br /><br />
<select name="paycheck">
	{% for paycheck in paychecks %}
	<option value="{{ paycheck.key }}">{{ paycheck.date }}</option>
	{% endfor %}
<input type="submit" value="Submit">
</form>
<br /><br />
{% endblock main %}

{% block form %}
<form action="" method="post">
  Date: <input type="text" name="date"><br />
  Name: <input type="text" name="name"><br />
  Description: <input type="text" name="description"><br />
  Amount: <input type="text" name="amount"><br />
  Frequency: <input type="text" name="freq"><br />
  Category: <input type="text" name="category"><br />
  <input type="submit" value="Submit">
</form>
{% endblock form %}