{% extends "base.tpl" %}

{% block headscript %}
<script>
function nameDisplay(fieldid, selectid) {
	var namefield = document.getElementById(fieldid);
	var typeselect = document.getElementById(selectid);
	var selection = typeselect.options[typeselect.selectedIndex].value;
	if (selection == "Other") {
		namefield.style.display = "block";
	}
	else {
		namefield.style.display = "none";
	}
}
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
		}
	}
}
</script>
{% endblock headscript %}

{% block headstyle %}
<style>
form.delete {
	display: inline;
	margin: 0;
	padding: 0;
}
form.delete button {
  background-color: transparent;
  border: none;
  border-bottom: solid blue 1px;
  color: blue;
  padding: 0px;
  cursor: pointer;
  font-size: 50%;
}
</style>
{% endblock headstyle %}

{% block main %}
<p><a href="/">Home</a> > {{ paycheck.date }} Paycheck</p>
<h2>{{ paycheck.date}} Paycheck</h2>
<p><strong>DEPOSIT ACCOUNT</strong>: {{ paycheck.dest_account.name }}</p>
<h3>Current Account Balances</h3>
<ul>
	{% for b in balances %}
	<li>{{ b.account.name }}: ${{ b.balance|floatformat:"2" }}
	{% endfor %}
</ul>
<p><strong>GROSS</strong>: ${{ paycheck.gross|floatformat:"2" }}</p>
<h3>Taxes</h3>
<ul>
	<li><strong>FEDERAL:</strong> {% if federal_tax %}${{ federal_tax.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ federal_tax.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
  <li><strong>STATE:</strong> {% if state_tax %}${{ state_tax.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ state_tax.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
  {% if other_taxes %}
  {% for tax in other_taxes %}
	<li>{{ tax.name }}: ${{ tax.amount|floatformat:"2"}}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ tax.key.name }}" /><button type="submit">Delete</button></form></li>
	{% endfor %}
	{% else %}
	<li><em>No other taxes entered</em></li>
	{% endif %}
</ul>
<p><strong>Total taxes:</strong> ${{ tax_total|floatformat:"2" }}</p>
<form action="" method="post">
  Type: <select name="tax-type" id="taxtypeselect" onchange="a='taxname';b='taxtypeselect';nameDisplay(a,b);">
	        {% if federal_tax %}{% else %}<option value="Federal">Federal</option>{% endif %}
	        {% if state_tax %}{% else %}<option value="State">State</option>{% endif %}
	        <option value="Other">Other</option>
	      </select><br />
	<div id="tax-name" style="display:none">Name: <input type="text" name="tax-name"><br /></div>
  Amount: <input type="text" name="tax-amount">
  <input type="submit" value="Submit">
</form>
<h3>Deductions</h3>
<ul>
	<li><strong>MEDICAL:</strong> {% if med_insurance %}${{ med_insurance.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ med_insurance.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
	<li><strong>DENTAL:</strong> {% if dental_insurance %}${{ dental_insurance.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ dental_insurance.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
	<li><strong>LIFE:</strong> {% if life_insurance %}${{ life_insurance.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ life_insurance.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
	<li><strong>VISION:</strong> {% if vision_insurance %}${{ vision_insurance.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ vision_insurance.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
	<li><strong>401k:</strong> {% if 401k %}${{ 401k.amount|floatformat:"2" }}  <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ 401k.key.name }}" /><button type="submit">Delete</button></form>{% else %}<em>Not entered</em>{% endif %}
  {% if deductions %}
  {% for d in deductions %}
	<li>{{ d.name }}: ${{ d.amount|floatformat:"2"}} <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ d.key.name }}" /><button type="submit">Delete</button></form></li>
	{% endfor %}
	{% else %}
	<li><em>No other deductions entered</em></li>
	{% endif %}
</ul>
<p><strong>Total deductions:</strong> ${{ deductions_total|floatformat:"2" }}</p>
<form action="" method="post">
  Type: <select name="deduction-type" id="deducttypeselect" onchange="a='deductname';b='deducttypeselect';nameDisplay(a,b);">
	        {% if med_insurance %}{% else %}<option value="Medical">Medical</option>{% endif %}
	        {% if dental_insurance %}{% else %}<option value="Dental">Dental</option>{% endif %}
	        {% if life_insurance %}{% else %}<option value="Life">Life</option>{% endif %}
	        {% if vision_insurance %}{% else %}<option value="Vision">Vision</option>{% endif %}
	        <option value="Other">Other</option>
	      </select><br />
	<div id="deductname" style="display:none">Name: <input type="text" id="dname" name="deduction-name"><br /></div>
  Amount: <input type="text" name="deduction-amount">
  <input type="submit" value="Submit">
</form>
<p><strong>AFTER DEDUCTIONS</strong>: ${{ paycheck.after_deduction_balance|floatformat:"2" }}</p>
<h3>Other Deposits</h3>
<ul>
	{% for d in deposits %}
	<li><strong>{{ d.source }}:</strong> ${{ d.amount|floatformat:"2"}} - {{ d.description }} <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ d.key.name }}" /><button type="submit">Delete</button></form> {% if d.verified %}<strong style="font-size:50%;">VERIFIED</strong>{% else %}<form class="delete" action="" method="post"><input type="hidden" name="verify-key" value="{{ d.key.name }}" /><button type="submit">Verify</button></form>{% endif %}</li>
	{% empty %}
	<li>No deposits entered.</li>
	{% endfor %}
</ul>
<p><strong>Total deposits:</strong> ${{ deposits_total|floatformat:"2" }}</p>
<form action="" method="post">
	Source: <input type="text" name="deposit-source"><br />
  Amount: <input type="text" name="deposit-amount"><br />
  Date: <input type="text" name="deposit-date"><br />
  Description: <input type="text" name="deposit-description"><br />
	<input type="submit" value="Submit">
</form>
<h3>Transfers</h3>
<ul>
  {% for t in transfers %}
	<li><strong>{{ t.receiving_account.name }}:</strong> ${{ t.amount|floatformat:"2"}} - {{ t.description }} <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ t.key.name }}" /><button type="submit">Delete</button></form> {% if t.verified %}<strong style="font-size:50%;">VERIFIED</strong>{% else %}<form class="delete" action="" method="post"><input type="hidden" name="verify-key" value="{{ t.key.name }}" /><button type="submit">Verify</button></form>{% endif %}</li>
	{% empty %}
	<li>No transfers entered</li>
	{% endfor %}
</ul>
<p><strong>Total transfers:</strong> ${{ transfers_total|floatformat:"2" }}</p>
<form action="" method="post">
  Account: <select name="transfer-account" id="transferaccountselect">
	           {% for account in accounts|dictsort:"name" %}
	           <option value="{{ account.key.name }}">{{ account.name }}</option>
	           {% endfor %}
	         </select><br />
  Amount: <input type="text" name="transfer-amount"><br />
  Date: <input type="text" name="transfer-date"><br />
  Description: <input type="text" name="transfer-description"><br />
	<input type="submit" value="Submit">
</form>
<p><strong>AFTER TRANSFERS</strong>: ${{ paycheck.after_transfer_balance|floatformat:"2" }}</p>
<h3>Expenses</h3>
<ul>
	<li>Food &amp; Dining: ${{ food_expenses_total|floatformat:"2" }}
		<ul>
			{% for expense in food_expenses|dictsort:"date" %}
			<li>{{ expense.date }} - {{ expense.vendor }}: ${{ expense.amount|floatformat:"2" }} <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ expense.key.name }}" /><button type="submit">Delete</button></form> {% if expense.verified %}<strong style="font-size:50%;">VERIFIED</strong>{% else %}<form class="delete" action="" method="post"><input type="hidden" name="verify-key" value="{{ expense.key.name }}" /><button type="submit">Verify</button></form>{% endif %}</li>
			{% empty %}
			<li><em>No food expenses entered.</em></li>
			{% endfor %}
		</ul>
	</li>
  <li>Other Expenses: ${{ other_expenses_total|floatformat:"2" }}
	  <ul>
    {% for expense in other_expenses|dictsort:"date" %}
	    <li>{{ expense.date }} - {{ expense.vendor }}: ${{ expense.amount|floatformat:"2"}} <form class="delete" action="" method="post"><input type="hidden" name="delete-key" value="{{ expense.key.name }}" /><button type="submit">Delete</button></form> {% if expense.verified %}<strong style="font-size:50%;">VERIFIED</strong>{% else %}<form class="delete" action="" method="post"><input type="hidden" name="verify-key" value="{{ expense.key.name }}" /><button type="submit">Verify</button></form>{% endif %}</li>
	  {% empty %}
			<li><em>No other expenses entered.</em></li>
	  {% endfor %}
	  </ul>
</ul>
<p><strong>Total expenses:</strong> ${{ all_expenses_total|floatformat:"2" }}</p>
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
		            <option value="{{ cat.key.name }}" {% if forloop.counter == 1 %}selected="selected"{% endif %}>{{ cat.name }}</option>
		          {% endfor %}
		          </select>
		        {% endfor %}<br />
  <input type="submit" value="Submit">
</form>
<p><strong>FINAL PAYCHECK BALANCE</strong>: ${{ paycheck.final_balance|floatformat:"2" }}</p>
{% endblock main %}

{% block javascript %}
<script>
  var namefields = new Array('tax-name', 'deductname');
  var selectfields = new Array('taxtypeselect', 'deducttypeselect');
  for (i=0; i < namefields.length; i++) {
	  nameDisplay(namefields[i], selectfields[i]);
  }
  subcatSelectionDisplay();
</script>
{% endblock javascript %}