<p>{% if doc.po_date %}
  Attention: The Customer's Purchase Order Date for Sales Order {{ doc.name }} has exceeded 5 months.
</p>

<p>We would like to inform you that the Purchase Order date for Sales Order {{ doc.name }} associated with the customer {{ doc.customer_name }} has surpassed the allowable 5-month period.</p>

<p>Please review the order details and take the necessary actions as soon as possible to ensure smooth processing and avoid further delays. If this order requires an update or further follow-up, kindly reach out to the customer or the relevant department.</p>

<p><strong>Order Details:</strong><br>
  - <strong>Sales Order ID:</strong> {{ doc.name }}<br>
  - <strong>Customer Name:</strong> {{ doc.customer_name }}<br>
  - <strong>Customer PO Date:</strong> {{ doc.po_date }}<br>
  - <strong>Days Exceeded:</strong> {{ (nowdate() | date_diff(doc.po_date)) - 150 }} days
</p>

<p>For any assistance or inquiries, feel free to contact the sales team or support.</p>

<p>Thank you for your prompt attention to this matter.</p>

<p>{% else %}</p>

<p>Customer's Purchase Order Date is not available for Sales Order {{ doc.name }}.</p>

<p>{% endif %}</p>
