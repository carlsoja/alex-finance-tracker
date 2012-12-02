{% extends "base.tpl" %}

{% block headscript %}
<script>
function taxNameDisplay() {
	var namefield = document.getElementById("taxname");
	var typeselect = document.getElementById("typeselect");
	var selection = typeselect.options[typeselect.selectedIndex].value;
	if (selection == "federal") {
	  namefield.style.display = "none";
	}
	else if (selection == "state") {
	  namefield.style.display = "none";
	}
	else {
	  namefield.style.display = "block";
	}
}

function deductionTypeDisplay() {
	var deduct_type_form = document.getElementById("deducttype");
	var expense_cats = document.getElementById("expensecat");
	var deposit_cats = document.getElementById("depositcat");
	
	var type_selection = deduct_type_form.options[deduct_type_form.selectedIndex].value;
	if (type_selection == "expense") {
		expense_cats.style.display = "block";
		deposit_cats.style.display = "none";
	}
	else if (type_selection == "deposit") {
		expense_cats.style.display = "none";
		deposit_cats.style.display = "block";
	}
	else {
		expense_cats.style.display = "none";
		deposit_cats.style.display = "none";
	}
}

function deductionNameDisplay() {
	var expense_cats = document.getElementById("expensecats");
	var deposit_cats = document.getElementById("depositcats");
	var expense_selection = expense_cats.options[expense_cats.selectedIndex].value;
	var deposit_selection = deposit_cats.options[deposit_cats.selectedIndex].value;
	var deductname = document.getElementById("deductname");
	if (expense_selection == "other" || deposit_selection == "other") {
		deductname.style.display = "block";
	}
	else {
		deductname.style.display = "none";
	}
}
</script>
{% endblock headscript %}

{% block main %}
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
  Type: <select name="tax-type" id="typeselect" onchange="taxNameDisplay()">
	        {% if federal_tax %}{% else %}<option value="federal">Federal</option>{% endif %}
	        {% if state_tax %}{% else %}<option value="state">State</option>{% endif %}
	        <option value="other">Other</option>
	      </select><br />
	<div id="taxname" style="display:none">Name: <input type="text" name="tax-name"><br /></div>
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
  Amount: <input type="text" name="deduction-amount"><br />
  Type: <select name="deduction-type" id="deducttype" onchange="deductionTypeDisplay()">
	        <option value="expense">Expense</option>
	        <option value="deposit">Deposit</option>
	      </select><br />
	<div id="expensecat" style="display:none">
		Expense Category: <select name="deduction-ecat" id="expensecats" onchange="deductionNameDisplay()">
		            <option value="health">Health</option>
		            <option value="dental">Dental</option>
		            <option value="vision">Vision</option>
		            <option value="life">Life</option>
		            <option value="gym">Gym</option>
		            <option value="other">Other</option>
		          </select><br />
	</div>
	<div id="depositcat" style="display:none">
		Deposit Category: <select name="deduction-dcat" id="depositcats" onchange="deductionNameDisplay()">
			                  <option value="401k">401(k)</option>
			                  <option value="internet">Internet Reimbursement</option>
			                  <option value="other">Other</option>
			                </select><br />
	</div>
	<div id="deductname" style="display:none">Name: <input type="text" name="deduction-name"><br /></div>
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

{% block javascript %}
<script>
  taxNameDisplay();
  deductionTypeDisplay();
  deductionNameDisplay();
</script>
{% endblock javascript %}