{% extends "base.tpl" %}

{% block headscript %}
<script>
function nameDisplay(fieldid, selectid) {
	var namefield = document.getElementById(fieldid);
	var typeselect = document.getElementById(selectid);
	var selection = typeselect.options[typeselect.selectedIndex].value;
	if (selection == "other") {
		namefield.style.display = "block";
	}
	else {
		namefield.style.display = "none";
	}
}
/*
function deductionTypeDisplay() {
	var deduct_type_form = document.getElementById("deducttype");
	var expense_cat = document.getElementById("expensecat");
	var deposit_cat = document.getElementById("depositcat");
	var expense_cats = document.getElementById("expensecats");
	var deposit_cats = document.getElementById("depositcats");
	
	var type_selection = deduct_type_form.options[deduct_type_form.selectedIndex].value;
	if (type_selection == "expense") {
		expense_cat.style.display = "block";
		deposit_cat.style.display = "none";
		deposit_cats.selectedIndex = 0;
	}
	else if (type_selection == "deposit") {
		expense_cat.style.display = "none";
		deposit_cat.style.display = "block";
	  expense_cats.selectedIndex = 0;
	}
	else {
		expense_cat.style.display = "none";
		deposit_cat.style.display = "none";
		expense_cats.selectedIndex = 0;
		deposit_cats.selectedIndex = 0;
	}
}
*/
</script>
{% endblock headscript %}

{% block main %}
<p><a href="/">Home</a> > {{ paycheck.date }} Paycheck</p>
<h2>{{ paycheck.date}} Paycheck</h2>
<p><strong>GROSS</strong>: ${{ paycheck.gross|floatformat:"2" }}</p>
<p>Taxes:</p>
<ul>
	<li><strong>FEDERAL:</strong> {% if federal_tax %}${{ federal_tax.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  <li><strong>STATE:</strong> {% if state_tax %}${{ state_tax.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  {% if other_taxes %}
  {% for tax in other_taxes %}
	<li>{{ tax.name }}: ${{ tax.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li><em>No other taxes entered</em></li>
	{% endif %}
</ul>
<p><strong>Total taxes:</strong> ${{ tax_total|floatformat:"2" }}</p>
<form action="" method="post">
  Type: <select name="tax-type" id="taxtypeselect" onchange="a='taxname';b='taxtypeselect';nameDisplay(a,b);">
	        {% if federal_tax %}{% else %}<option value="federal">Federal</option>{% endif %}
	        {% if state_tax %}{% else %}<option value="state">State</option>{% endif %}
	        <option value="other">Other</option>
	      </select><br />
	<div id="taxname" style="display:none">Name: <input type="text" name="tax-name"><br /></div>
  Amount: <input type="text" name="tax-amount">
  <input type="submit" value="Submit">
</form>
<p>Deductions:</p>
<ul>
	<li><strong>MEDICAL:</strong> {% if med_insurance %}${{ med_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>DENTAL:</strong> {% if dental_insurance %}${{ dental_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>LIFE:</strong> {% if life_insurance %}${{ life_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>VISION:</strong> {% if vision_insurance %}${{ vision_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>401k:</strong> {% if 401k %}${{ 401k.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  {% if deductions %}
  {% for d in deductions %}
	<li>{{ d.name }}: ${{ d.amount|floatformat:"2"}}</li>
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
	        {% if 401k %}{% else %}<option value="401k">401k</option>{% endif %}
	        <option value="other">Other</option>
	      </select><br />
	<div id="deductname" style="display:none">Name: <input type="text" id="dname" name="deduction-name"><br /></div>
  Amount: <input type="text" name="deduction-amount">
  <input type="submit" value="Submit">
</form>
<p><strong>AFTER DEDUCTIONS</strong>: ${{ paycheck.after_deduction_balance|floatformat:"2" }}</p>
<p>Deposits:</p>
<ul>
  {% for d in deposits %}
	<li>{{ d.receiving_account.name }}: ${{ d.amount|floatformat:"2"}} - {{ d.description }}</li>
	{% empty %}
	<li>No deposits entered</li>
	{% endfor %}
</ul>
<p><strong>Total deposits:</strong> ${{ deposits_total|floatformat:"2" }}</p>
<form action="" method="post">
  Account: <select name="deposit-account" id="depositaccountselect">
	           {% for account in accounts|dictsort:"name" %}
	           <option value="{{ account.key.name }}">{{ account.name }}</option>
	           {% endfor %}
	         </select><br />
  Amount: <input type="text" name="deposit-amount"><br />
  Date: <input type="text" name="deposit-date"><br />
  Description: <input type="text" name="deposit-description"><br />
	<input type="submit" value="Submit">
</form>
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
<form action="" method="post">
  Name: <input type="text" name="expense-name"><br />
  Description: <input type="text" name="expense-description"><br />
  Amount: <input type="text" name="expense-amount"><br />
  Category: <input type="text" name="expense-category">
  <input type="submit" value="Submit">
</form>
<p><strong>FINAL PAYCHECK BALANCE</strong>: ${{ paycheck.final_balance|floatformat:"2" }}</p>
{% endblock main %}

{% block javascript %}
<script>
  var namefields = new Array('taxname', 'deductname');
  var selectfields = new Array('taxtypeselect', 'deducttypeselect');
  for (i=0; i < namefields.length; i++) {
	  nameDisplay(namefields[i], selectfields[i]);
  }
  /*deductionTypeDisplay();*/
</script>
{% endblock javascript %}