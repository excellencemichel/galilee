# Checkout Process

1. Cart -> Checkout view
	?
	- Login/Register or Enter an Email (as Gest)
	- Shipping Address
	- Billing Info
		- Billing Address
		- Credit Card / Payment



2. Billing App/Component
	- Billing Profile
		- User or Email (Gest Email)
		- generate payment processor token (Stripe or Braintree)


3. Orders / Invoices Component
	- Connecting the Billing Profile
	- Shipping / Billing Address
	- Cart
	- Status --Shipped ? Cancelled ?




4. Backup fixtures
python manager.py dupdata products --format json --indent 4 > products/fixtures/products.json #Pour stocker les données dans le json

5. ./manage.py loaddata products/fixtures/products.json # Pour recharger les données déja stocker dans le json