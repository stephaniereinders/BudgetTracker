from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from os import path


class BudgetTracker:
    def __init__(self, starting_balance, start_date, transactions_notebook_name):
        """Create a new BudgetTracker. Enter the account's starting balance. The balance can be $0. The start date
        should be formatted as 'YYYY-MM-DD'. Choose the name you would like to use for the transaction notebook. The
        notebook will be saved as a csv file under this name."""

        self.balance = round(starting_balance, 2)
        self.current_date = date.fromisoformat(start_date)

        # Start transactions notebook
        self.transactions_filename = transactions_notebook_name + '.csv'
        self.transactions = self.__start_transactions_notebook()

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
        self.budget = {'housing': 0.25,
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
            ax1.text(bar.get_width() + 25, bar.get_y() + (bar.get_height() / 2),
                     value, ha='center', va='center')

        plt.show()

    def show_budget_pie_chart(self):
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

    def show_transactions_notebook(self):
        """Display the transactions notebook."""
        print("TRANSACTIONS NOTEBOOK:")
        print("-------------------------")
        print(self.transactions)

    def allocate(self, amount):
        """Allocate the amount (rounded to the nearest cent) to the budget categories."""
        for category in self.category_balances:
            portion = round(amount * self.budget[category], 2)
            self.category_balances[category] += portion

    def change_budget(self, budget_dict):
        """Change the budget categories and allocation amounts. The budget_dict should be a Python dictionary where
        the keys are the budget category names and the values are the corresponding allocation amounts. The allocation
        amount should be decimals between 0 and 1 and their sum should equal 1. As an example,
        budget_dict = {'Housing': 0.5, 'Food': 0.25, 'Clothing': 0.25'} could be your new budget."""
        if round(sum(budget_dict.values()), 2) != 1:
            print("The allocation amounts do not sum to 1. The current total is",
                  round(sum(budget_dict.values()), 2))
            return
        else:
            self.budget = budget_dict
            # Update the category names and set the category balances to zero
            self.category_balances = {key: 0 for key in self.budget}
            # Allocate the current balance to using the new budget
            self.allocate(amount=self.balance)
            print("The new budget has been set and the current balance has been reallocated to the budget categories "
                  "accordingly. Here are the new budget category balances:")
            self.show_balance_barchart()

    def withdraw(self, withdrawal_date, withdrawal_category, withdrawal_amount):
        """Withdraw money from the account. This subtracts the withdrawal amount from the account balance and the
        withdrawal budget category balance, and add this transaction to the transactions notebook. The deposit date
        should be formatted as 'YYYY-MM-DD'."""
        self.balance -= round(withdrawal_amount, 2)
        self.category_balances[withdrawal_category] -= withdrawal_amount
        self.__update_register(transaction_date=withdrawal_date,
                               transaction_type='withdrawal',
                               budget_category=withdrawal_category,
                               transaction_amount=withdrawal_amount)

    def deposit(self, deposit_date, deposit_amount):
        """Deposit money into the account. This adds the deposit amount to the account balance, allocates the amount
        across the various budget categories, and adds this transaction to the transactions notebook. The deposit date
        should be formatted as 'YYYY-MM-DD'."""
        self.balance += round(deposit_amount, 2)
        self.allocate(amount=deposit_amount)
        self.__update_register(transaction_date=deposit_date,
                               transaction_type='deposit',
                               budget_category='all',
                               transaction_amount=deposit_amount)

    def __start_transactions_notebook(self):
        """Start a notebook of transactions as a Pandas DataFrame and save as a csv file. If a csv file by that name
        already exists in the directory, ask the user if they want to overwrite it or choose a different name."""

        # If file already exists, let the user overwrite it or choose a new name.
        if path.exists(self.transactions_filename):
            if input(f'{self.transactions_filename} already exists. Do you want to use this file as your transactions '
                     f'notebook? (y/n): ') not in ['y', 'yes', 'Y', 'Yes', 'YES']:
                self.transactions_filename = input("Choose a new filename. Example 'transactions1.csv': ")

        # Create a DataFrame of the transactions
        self.transactions = pd.DataFrame(data=[[self.current_date, 'starting balance', 'none', 0, self.balance]],
                                         columns=['transaction_date', 'transaction_type', 'budget_category',
                                                  'transaction_amount', 'current_balance'])
        # Save DataFrame to csv
        self.transactions.to_csv(self.transactions_filename)

        return self.transactions

    def __update_register(self, transaction_date, transaction_type, budget_category, transaction_amount):
        """Add a new transaction to the transactions notebook. The transaction date should be formatted as
        'YYYY-MM-DD'."""
        transaction = [{'transaction_date': transaction_date,
                        'transaction_type': transaction_type,
                        'budget_category': budget_category,
                        'transaction_amount': transaction_amount,
                        'current_balance': self.balance}]
        self.transactions = self.transactions.append(transaction)
        self.transactions.to_csv(self.transactions_filename, index=False)
