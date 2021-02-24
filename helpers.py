from datetime import date
import pandas as pd


class Account:
    def __init__(self, starting_balance, start_date):
        self.balance = round(starting_balance, 2)
        self.current_date = date.fromisoformat(start_date)
        self.check_register = None

        # Allocate balance to budget categories
        self.allocations = {'housing': 0.3,
                            'food': 0.2,
                            'car': 0.25,
                            'clothing': 0.1,
                            'entertainment': 0.1,
                            'other': 0.05}
        self.categories = {'housing': round(starting_balance * self.allocations['housing'], 2),
                           'food': round(starting_balance * self.allocations['food'], 2),
                           'car': round(starting_balance * self.allocations['car'], 2),
                           'clothing': round(starting_balance * self.allocations['clothing'], 2),
                           'entertainment': round(starting_balance * self.allocations['entertainment'], 2),
                           'other': round(starting_balance * self.allocations['other'], 2)}

        # Rounding amounts to whole cents can cause the sum of the category balances to be different than the total
        # balance. Either add or subtract the difference between the sum of the categories and the total balance from
        # the Other category so that the sum and the balance are equal.
        self.categories['other'] += self.balance - sum(self.categories.values())

    def start_check_register(self):
        """Start a check register as a Pandas DataFrame and save as a csv file"""
        self.check_register = pd.DataFrame(data=[[self.current_date, 'starting balance', 'none', 0, self.balance]],
                                           columns=['transaction_date', 'transaction_type', 'budget_category',
                                                    'transaction_amount', 'current_balance'])
        self.check_register.to_csv('check_register.csv')

    def allocate(self, amount):
        """Allocate deposit to various budget categories, rounding each amount to a whole number of cents. Put all
        unallocated money, roughly 0.05% into the Other category."""
        self.categories['other'] += amount  # start by adding the total amount to the Other category
        for category in self.categories:
            # For each category except other, add a portion of the amount to the category and subtract that amount from
            # the Other category.
            if category != 'other':
                self.categories[category] += round(amount * self.allocations[category], 2)
                self.categories['other'] -= round(amount * self.allocations[category], 2)
        # Rounding amounts to whole cents can cause the sum of the category balances to be different than the total
        # balance. Either add or subtract the difference between the sum of the categories and the total balance from
        # the Other category so that the sum and the balance are equal.
        self.categories['other'] += self.balance - sum(self.categories.values())

    def show_balance(self):
        """Show the current balance of the account and the balance for each budget category."""
        print("Total balance: ${:,.2f}".format(self.balance))
        [print("{:} balance: ${:,.2f}".format(category, self.categories[category])) for category in self.categories]

    def show_check_register(self):
        """Display the check register."""
        print("Check register:\n", self.check_register)

    def update_register(self, transaction_date, transaction_type, budget_category, transaction_amount):
        transaction = [{'transaction_date': transaction_date,
                        'transaction_type': transaction_type,
                        'budget_category': budget_category,
                        'transaction_amount': transaction_amount,
                        'current_balance': self.balance}]
        self.check_register = self.check_register.append(transaction)
        self.check_register.to_csv('check_register.csv', index=False)

    def withdraw(self, withdrawal_date, withdrawal_category, withdrawal_amount):
        self.balance -= withdrawal_amount
        self.categories[withdrawal_category] -= withdrawal_amount
        self.update_register(transaction_date=withdrawal_date,
                             transaction_type='withdrawal',
                             budget_category=withdrawal_category,
                             transaction_amount=withdrawal_amount)

    def deposit(self, deposit_date, deposit_amount):
        """Deposit money into the account, update the check register, and allocate the deposit to the various budget
        categories."""
        self.balance += deposit_amount
        self.allocate(amount=deposit_amount)
        self.update_register(transaction_date=deposit_date,
                             transaction_type='deposit',
                             budget_category='all',
                             transaction_amount=deposit_amount)
