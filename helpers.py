from datetime import date
import pandas as pd
import matplotlib.pyplot as plt


class BudgetTracker:
    def __init__(self, starting_balance, start_date):
        self.balance = round(starting_balance, 2)
        self.current_date = date.fromisoformat(start_date)
        self.check_register = None

        # Allocate balance to budget categories
        self.category_balances = {'housing': 0,
                                  'insurance': 0,
                                  'food': 0,
                                  'transportation': 0,
                                  'utilities': 0,
                                  'savings': 0,
                                  'entertainment': 0,
                                  'clothing': 0,
                                  'miscellaneous': 0}
        self.allocations = {'housing': 0.25,
                            'insurance': 0.1,
                            'food': 0.1,
                            'transportation': 0.1,
                            'utilities': 0.1,
                            'savings': 0.1,
                            'entertainment': 0.1,
                            'clothing': 0.05,
                            'miscellaneous': 0.1}
        self.allocate(amount=self.balance)

    def show_balance(self):
        """Show the current balance of the account and the balance for each budget category."""
        print("TOTAL BALANCE: ${:,.2f}".format(self.balance))
        print("-------------------------")
        [print("{:} balance: ${:,.2f}".format(category, self.category_balances[category]))
         for category in self.category_balances]

    def show_balance_barchart(self):
        """Create a (horizontal) barchart that shows the balance of each of the budget categories."""

        # Round all balances to the nearest cent
        rounded_balances = dict(map(lambda x: (x[0], round(x[1], 2)), self.category_balances.items()))
        keys = list(rounded_balances.keys())
        values = rounded_balances.values()

        # Create plot
        fig1, ax1 = plt.subplots()
        ax1.barh(keys, values)

        # Label plot and axes
        ax1.set_xlabel('Dollars ($)')
        ax1.set_ylabel('Budget Category')
        ax1.set_title('Budget Category Balances')

        # Show the category balance to the right of every bar
        bars = ax1.patches
        for bar, value in zip(bars, values):
            ax1.text(bar.get_width() + 25, bar.get_y() + (bar.get_height()/2),
                     value, ha='center', va='center')

        plt.show()

    def allocate(self, amount):
        """Allocate amount (rounded to the nearest cent) to various budget categories, rounding each amount to a whole
        number of cents. If rounding causes the sum of the category balances to be greater than the total balance,
        subtract the difference from the Miscellaneous category and round the Miscellaneous category balance down to
        the nearest cent."""

        # Add the amount to the Miscellaneous category
        self.category_balances['miscellaneous'] += round(amount, 2)
        # For each category except other, add a portion of the amount to the category and subtract that amount from
        # the Other category.
        for category in self.category_balances:
            if category != 'miscellaneous':
                portion = round(amount * self.allocations[category], 2)
                self.category_balances[category] += portion
                self.category_balances['miscellaneous'] -= portion
        # Adjust the balance of the Other category so that the sum of all category balances is less than or equal to
        # the total balance.
        if self.balance < sum(self.category_balances.values()):
            self.category_balances['miscellaneous'] -= self.balance - sum(self.category_balances.values())
            self.category_balances['miscellaneous'] = round(self.category_balances['miscellaneous'], 2)

    def show_allocations_pie_chart(self):
        """Create a pie chart that shows how money will be allocated to the various budget categories."""

        # Create pie chart
        sizes = self.category_balances.values()
        labels = self.category_balances.keys()
        fig2, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Label plot and axes
        ax1.set_title('Budget Category Allocations')

        plt.show()

    def start_check_register(self):
        """Start a check register as a Pandas DataFrame and save as a csv file"""
        self.check_register = pd.DataFrame(data=[[self.current_date, 'starting balance', 'none', 0, self.balance]],
                                           columns=['transaction_date', 'transaction_type', 'budget_category',
                                                    'transaction_amount', 'current_balance'])
        self.check_register.to_csv('check_register.csv')

    def show_check_register(self):
        """Display the check register."""
        print("Check register:\n", self.check_register)

    def update_register(self, transaction_date, transaction_type, budget_category, transaction_amount):
        """Add a new transaction to the check register. The transaction date should be formatted as 'YYYY-MM-DD'."""
        transaction = [{'transaction_date': transaction_date,
                        'transaction_type': transaction_type,
                        'budget_category': budget_category,
                        'transaction_amount': transaction_amount,
                        'current_balance': self.balance}]
        self.check_register = self.check_register.append(transaction)
        self.check_register.to_csv('check_register.csv', index=False)

    def withdraw(self, withdrawal_date, withdrawal_category, withdrawal_amount):
        """Withdraw money from the account. This subtracts the withdrawal amount from the account balance and the
        withdrawal budget category balance, and add this transaction to the check register. The deposit date should be
        formatted as 'YYYY-MM-DD'."""
        self.balance -= round(withdrawal_amount, 2)
        self.category_balances[withdrawal_category] -= withdrawal_amount
        self.update_register(transaction_date=withdrawal_date,
                             transaction_type='withdrawal',
                             budget_category=withdrawal_category,
                             transaction_amount=withdrawal_amount)

    def deposit(self, deposit_date, deposit_amount):
        """Deposit money into the account. This adds the deposit amount to the account balance, allocates the amount
        across the various budget categories, and adds this transaction to the check register. The deposit date should
        be formatted as 'YYYY-MM-DD'."""
        self.balance += round(deposit_amount, 2)
        self.allocate(amount=deposit_amount)
        self.update_register(transaction_date=deposit_date,
                             transaction_type='deposit',
                             budget_category='all',
                             transaction_amount=deposit_amount)
