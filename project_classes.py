import datetime
import os

class User:
    def __init__(self, username):
        """
        Initialize a User object.

        :param username: The username of the user.
        """
        self.username = username
    
class Vault:
    def __init__(self, vault_id, vault_name, start, end, user):
        """
        Initialize a Vault object.

        :param vault_id: The ID of the vault (must be an integer).
        :param vault_name: The name of the vault.
        :param start: The start date of the vault (must be a datetime.date object).
        :param end: The end date of the vault (must be a datetime.date object).
        :param username: The username of the user associated with the vault (optional).
                       If not provided, it will use the username from the User class.
        """

        # Validations
        if not isinstance(vault_id, int):
            raise ValueError("ID must be an integer value!")

        if not isinstance(start, datetime.date):
            raise ValueError("start must be a valid date object!")

        if not isinstance(end, datetime.date):
            raise ValueError("end must be a valid date object!")

        if start > end:
            raise ValueError("start date cannot be later than end date!")
        
        if not isinstance(user, User):  # Validate that user is a User object
            raise ValueError("user must be an instance of the User class!")

        # Assign to self object
        self.vault_id = vault_id
        self.vault_name = vault_name
        self.start = start
        self.end = end
        self.user = user # Composition used instead of inheritence: Vault has a User object instance
        self.username = user.username # variable to store username as a string (not the object instance)
        self.pots = []  # List to store associated Pot instances

    def __str__(self):
        return f"Vault(vault_id={self.vault_id}, vault_name={self.vault_name}, start={self.start}, end={self.end}, username={self.username})"
    
    def add_pot(self, pot):
        """
        Add a Pot instance to the Vault's list of pots.

        :param pot: The Pot instance to add.
        """
        if not isinstance(pot, Pot):
            raise ValueError("pot must be an instance of the Pot class!")
        self.pots.append(pot)

    def vault_value(self):
        """
        Sum the amounts of all Pot instances associated with this Vault.

        :return: The sum of the amounts of all pots.
        """
        sum = 0
        if len(self.pots) > 0:
            for pot in self.pots:
                sum += pot.amount
        return sum
    
class Pot:
    def __init__(self, pot_id, pot_name, start, end, vault, user, amount=0.00):
        """
        Initialize a Pot object.

        :param pot_id: The ID of the pot (must be an integer and unique to Pot).
        :param pot_name: The name of the pot.
        :param start: The start date of the pot (must be a datetime.date object).
        :param end: The end date of the pot (must be a datetime.date object).
        :param vault: The Vault object associated with the pot.
        :param username: The username of the user associated with the pot (optional).
        :param amount: The amount of the pot. Default is 0.00.
        """

        # Validations
        if not isinstance(pot_id, int):
            raise ValueError("Pot ID must be an integer value!")

        if not isinstance(start, datetime.date):
            raise ValueError("start must be a valid date object!")

        if not isinstance(end, datetime.date):
            raise ValueError("end must be a valid date object!")

        if start > end:
            raise ValueError("start date cannot be later than end date!")
        
        if not isinstance(vault, Vault):  # Validate that vault is a Vault object
            raise ValueError("vault must be an instance of the Vault class!")
        
         # Assign unique Pot attributes
        self.pot_id = pot_id
        self.pot_name = pot_name
        self.start = start
        self.end = end
        self.vault = vault  # Composition used instead of inheritence: Pot has a Vault object instance
        self.vault_id = vault.vault_id # vault_id as string
        self.amount = amount
        self.transactions = [] # List only contains transactions that need processing (i.e. subtracting or adding from pot amount)
        self.user = user # Composition used instead of inheritence: Vault has a User object instance
        self.username = user.username # variable to store username as a string (not the object instance)

        # Add this Pot to the Vault's list of pots
        vault.add_pot(self)

    def add_transaction(self, transaction):
        """
        Add a transaction instance to the pots list of transactions.

        :param transaction: The transaction instance to add.
        """
        if not isinstance(transaction, Transaction):
            raise ValueError("transaction must be an instance of the Transaction class!")
        self.transactions.append(transaction)
    
    def pot_value(self):
        """
        Sum the amounts of all transaction instances associated with this Pot. Then subtract this from the pot_amount

        :return: The sum of the amounts of all pots.
        """
        sum = 0
        today = datetime.datetime.today()
        if len(self.transactions) > 0:
            for transaction in self.transactions:
                if transaction.date <= today:
                    sum += transaction.amount
                    self.amount += sum
                    self.transactions = []
        return 
            
class Transaction:
    def __init__(self, transaction_id, transaction_name, date, pot, user, type="out", amount=0.00):
        """
        Initialize a Transaction object.

        :param transaction_id: The ID of the transaction (must be an integer and unique to the transaction).
        :param transaction_name: Description of the transaction
        :param date: date the transaction occured
        :param amount: The amount of the transaction. Default is 0.00.
        """

        # Validations
        if not isinstance(transaction_id, int):
            raise ValueError("Transaction ID must be an integer value!")

        if not isinstance(date, datetime.date):
            raise ValueError("Must be a valid date object!")
        
        if not isinstance(pot, Pot):  # Validate that pot is a Pot object
            raise ValueError("pot must be an instance of the Pot class!")
        
        if type not in ["in", "out"]:
            raise ValueError('Transaction type must be either "in" or "out"!')
        
         # Assign unique Pot attributes
        self.transaction_id = transaction_id
        self.transaction_name = transaction_name
        self.date = date
        self.pot = pot  # Composition used instead of inheritence: Transaction has a Pot object instance
        self.pot_id = pot.pot_id # String of pot_id
        self.type = type
        self.amount = amount
        self.user = user # Composition used instead of inheritence: Vault has a User object instance
        self.username = user.username # variable to store username as a string (not the object instance)
        
        # Add this transaction to the pots list of transactions
        pot.add_transaction(self)
