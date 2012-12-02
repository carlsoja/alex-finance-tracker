{% extends "base.tpl" %}

{% block main %}
{% if accounts %}
<h2>Active Accounts</h2>
{% for account in accounts %}
<p><strong>{{ account.name }}</strong>: ${{ account.unv_balance|floatformat:"2" }} <em>(last verified {{ account.last_verified }})</em></p>
{% endfor %}
<p><strong>TOTAL</strong>: ${{ total|floatformat:"2" }}</p>
{% endif %}
{% if paychecks %}
<h2>Active Paychecks</h2>
{% for paycheck in paychecks %}
<p><strong><a href="/paycheck/detail/{{ paycheck.key }}">{{ paycheck.date }}</a></strong> - Gross: ${{ paycheck.gross|floatformat:"2" }}, Current Sub-Total: ${{ paycheck.final_balance|floatformat:"2" }}</p>
{% endfor %}
{% endif %}
<h2>Unassigned expenses</h2>
<form action="" method="post">
{% for expense in expenses %}
<input type="checkbox" name="expense{{ forloop.counter }}" value="{{ expense.key }}">{{ expense.date }}: {{ expense.name }}<br />
${{ expense.amount }}, {{ expense.frequency }}</input>
<br />
{% endfor %}
<br /><br />
<select name="paycheck">
	{% for paycheck in paychecks %}
	<option name="paycheck" value="{{ paycheck.key }}">{{ paycheck.date }}</option>
	{% endfor %}
</select>
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
  Account: <select name="account">
             {% for account in accounts %}
             <option name="{{ account.name }}" value="{{ account.key }}">{{ account.name }}</option>
             {% endfor %}
           </select><br />
  Frequency: <select name="freq">
	             <option name="One-Time" value="One-Time">One-Time</option>
	             <option name="Regular" value="Regular">Regular</option>
	             <option name="Core" value="Core">Core</option>
	           </select><br />
  Category: <input type="text" name="category"><br />
  <input type="submit" value="Submit">
</form>
{% endblock form %}