{% extends "base.tpl" %}

{% block headscript %}
<script>
function subcatSelectionDisplay() {
	var parentselect = document.getElementById("expense-parent-cat");
	var parent_selection = parentselect.options[parentselect.selectedIndex].value;
	var parentcatids = Array({% for group in child_cat_groups %}"{{ group.0.parent_cat.key.name }}"{% if forloop.counter != child_cat_groups|length %}, {% endif %}{% endfor %});
	for(i=0; i < parentcatids.length; i++){
		selector = document.getElementById(parentcatids[i]);
		if (parent_selection == parentcatids[i]) {
			selector.style.display = "block";
		}
		else {
			selector.style.display = "none";
			selector.options[selector.selectedIndex].value = null;
		}
	}
}
</script>
{% endblock headscript %}

{% block main %}
{% if accounts %}
<h2>Active Accounts</h2>
{% for account in accounts %}
<p><strong>{{ account.name }}</strong>: ${{ account.unv_balance|floatformat:"2" }} <em>(last verified {{ account.last_verified }})</em></p>
{% empty %}
<p><em>No accounts in the database.</em></p>
{% endfor %}
<p><strong>TOTAL</strong>: ${{ total|floatformat:"2" }}</p>
<p><strong><a href="account">Manage accounts</a></strong></p>
{% endif %}
{% if paychecks %}
<h2>Active Paychecks</h2>
{% for paycheck in paychecks %}
<p><strong><a href="/paycheck/detail/{{ paycheck.key }}">{{ paycheck.date }}</a></strong> - Gross: ${{ paycheck.gross|floatformat:"2" }}, Current Sub-Total: ${{ paycheck.final_balance|floatformat:"2" }}</p>
{% empty %}
<p><em>No paychecks in the database.</em></p>
{% endfor %}
<p><strong><a href="paycheck">Manage paychecks</a></strong></p>
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
  Vendor: <input type="text" name="expense-vendor"><br />
  Amount: <input type="text" name="expense-amount"><br />
  Date: <input type="text" name="expense-date"><br />
  Description: <input type="text" name="expense-description"><br />
  Account: <select name="expense-account">
	         {% for account in payment_accounts %}
	           <option value="{{ account.key.name }}">{{ account.name }}</option>
	         {% endfor %}
	         </select><br />
  Category: <select name="parent-cat" id="expense-parent-cat" onchange="subcatSelectionDisplay()">
	            {% for cat in parent_cats %}
	            <option value="{{ cat.key.name }}">{{ cat.name }}</option>
	            {% endfor %}
	          </select><br />
	          {% for group in child_cat_groups %}
	            <select name="child-{{ group.0.parent_cat.key.name }}" id="{{ group.0.parent_cat.key.name }}">
		          {% for cat in group %}
		            <option value="{{ cat.key.name }}">{{ cat.name }}</option>
		          {% endfor %}
		          </select>
		        {% endfor %}<br />
  <input type="submit" value="Submit">
</form>
<p><strong><a href="category">Manage categories</a></strong></p>
{% endblock form %}

{% block javascript %}
<script>
subcatSelectionDisplay();
</script>
{% endblock javascript %}