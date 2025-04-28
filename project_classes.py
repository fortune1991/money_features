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
    def __init__(self, vault_id, vault_name, user):
        """
        Initialize a Vault object.

        :param vault_id: The ID of the vault (must be an integer).
        :param vault_name: The name of the vault.
        :param username: The username of the user associated with the vault (optional).
                       If not provided, it will use the username from the User class.
        """

        # Validations
        if not isinstance(vault_id, int):
            raise ValueError("ID must be an integer value!")
        
        if not isinstance(user, User): 
            raise ValueError("user must be an instance of the User class!")

        # Assign to self object
        self.vault_id = vault_id
        self.vault_name = vault_name
        self.user = user 
        self.username = user.username 
        self.pots = []  

    def __str__(self):
        return f"Vault(vault_id={self.vault_id}, vault_name={self.vault_name}, username={self.username})"
    
    def add_pot(self, pot):
        """
        Add a Pot instance to the Vault's list of pots.

        :param pot: The Pot instance to add.
        """
        if not isinstance(pot, Pot):
            raise ValueError("pot must be an instance of the Pot class!")
        self.pots.append(pot)

    def vault_value(self):
        """Returns current value of vault (sum of all pot current values)"""
        return sum(pot.pot_value() for pot in self.pots)

    def vault_forecast_value(self, date):
        """
        Sum the amounts of all Pot instances associated with this Vault.

        :return: The sum of the amounts of all pots.
        """
        sum = 0
        
        if len(self.pots) > 0:
            for pot in self.pots:
                for forecast in pot.forecasts:
                    pot_value = pot.pot_forecast_value(date)
                    sum += pot_value
        return sum
    
class Pot:
    def __init__(self, pot_id, pot_name, vault, user, amount=0.00):
        """
        Initialize a Pot object.

        :param pot_id: The ID of the pot (must be an integer and unique to Pot).
        :param pot_name: The name of the pot.
        :param vault: The Vault object associated with the pot.
        :param username: The username of the user associated with the pot (optional).
        :param amount: The amount of the pot. Default is 0.00.
        """

        # Validations
        if not isinstance(pot_id, int):
            raise ValueError("Pot ID must be an integer value!")
        
        if not isinstance(vault, Vault): 
            raise ValueError("vault must be an instance of the Vault class!")
        
         # Assign unique Pot attributes
        self.pot_id = pot_id
        self.pot_name = pot_name
        self.vault = vault  
        self.vault_id = vault.vault_id 
        self.amount = amount
        self.transactions = [] 
        self.forecasts = [] 
        self.user = user 
        self.username = user.username 

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

    def add_forecast(self, forecast):
        """
        Add a forecast instance to the pots list of forecasts.

        :param forecast: The forecast instance to add.
        """
        if not isinstance(forecast, Forecast):
            raise ValueError("forecast must be an instance of the Forecast class!")
        self.forecasts.append(forecast)
    
    def pot_value(self):
        """Returns current value (base amount + transactions to date)"""
        total = self.amount
        today = datetime.datetime.today()
        for transaction in self.transactions:
            if transaction.date <= today:
                total += transaction.amount
        return total

    def pot_forecast_value(self, date):
        """Returns only future forecasts for this pot (no base amount, no transactions)"""
        forecast_total = 0
        for forecast in self.forecasts:
            if forecast.date <= date:
                forecast_total += forecast.amount
        return forecast_total
            
class Transaction:
    def __init__(self, transaction_id, transaction_name, date, pot, vault, user, type="out", amount=0.00):
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
        
        if not isinstance(pot, Pot): 
            raise ValueError("pot must be an instance of the Pot class!")
        
        if type not in ["in", "out"]:
            raise ValueError('Transaction type must be either "in" or "out"!')
        
         # Assign unique Pot attributes
        self.transaction_id = transaction_id
        self.transaction_name = transaction_name
        self.date = date
        self.pot = pot  
        self.pot_id = pot.pot_id 
        self.vault = vault  
        self.vault_id = vault.vault_id 
        self.type = type
        self.amount = amount
        self.user = user 
        self.username = user.username 
        
        # Add this transaction to the pots list of transactions
        pot.add_transaction(self)

class Forecast:
    def __init__(self, forecast_id, forecast_name, date, pot, vault, user, type="out", amount=0.00):
        """
        Initialize a Forecast object.

        :param transaction_id: The ID of the forecast (must be an integer and unique to the transaction).
        :param forecast_name: Description of the forecast
        :param date: date the forecast occured
        :param amount: The amount of the forecast. Default is 0.00.
        """

        # Validations
        if not isinstance(forecast_id, int):
            raise ValueError("Forecast ID must be an integer value!")

        if not isinstance(date, datetime.date):
            raise ValueError("Must be a valid date object!")
        
        if not isinstance(pot, Pot):  
            raise ValueError("pot must be an instance of the Pot class!")
        
        if type not in ["in", "out"]:
            raise ValueError('Forecast type must be either "in" or "out"!')
        
         # Assign unique Pot attributes
        self.forecast_id = forecast_id
        self.forecast_name = forecast_name
        self.date = date
        self.pot = pot  
        self.pot_id = pot.pot_id 
        self.vault = vault  
        self.vault_id = vault.vault_id 
        self.type = type
        self.amount = amount
        self.user = user 
        self.username = user.username 
        
        # Add this forecast to the pots list of forecasts
        pot.add_forecast(self)