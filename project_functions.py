import datetime,os,sqlite3
from project_classes import User,Vault,Pot,Transaction,Forecast
from tabulate import tabulate
from time import sleep

import warnings
warnings.filterwarnings("ignore",message="The default datetime adapter is deprecated",category=DeprecationWarning)

def submit_forecast(con,forecast_name,x,pot,vault,user,username,date,amount,forecast_type):
    forecast_id = x + 1
    #Input all information into the Class
    forecast = Forecast(forecast_id=forecast_id,forecast_name=forecast_name,date=date,pot=pot,vault=vault,type=forecast_type,amount=amount,user=user)
    forecast_data = [(forecast_id,forecast_name,date,pot.pot_id,vault.vault_id,forecast_type,amount,username)]
    if forecast:
        print_slow_nospace("\nThanks, your forecast has been created succesfully")
        # Save transaction to database
        cur = con.cursor()
        cur.executemany("INSERT INTO forecasts VALUES(?,?,?,?,?,?,?,?)",forecast_data)
        con.commit()
        cur.close()
    else:
        print_slow("ERROR: forecast not created succesfully")
    return forecast

def submit_transaction(con,x,pot,vault,user,username):
    print_slow("\nPlease provide a name reference for this transaction: ")
    transaction_name = input()
    transaction_id = x + 1
    today = datetime.datetime.today()
    print_slow("\nExcellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
    while True:
        date = collect_date("Date of transaction: ")
        if date <= today:
            break
        else:
            print_slow("\nTransactions cannot be submitted for the future. Please try again")
    # Collect transaction type
    while True:
        types = ["in","out"]
        print_slow('\nPlease define the type of transaction. "in" or "out": ')
        transaction_type = input()
        if transaction_type not in types:
            print_slow("\nincorrect transaction reference")
        else:
            break
    # Collect transaction amount
    print_slow("\nWhat is the transaction amount?: ")
    while True:
        amount = int_validator()
        if amount > 0:
            break
        else:
            print_slow("\namount must be greater than 0")

    if transaction_type == "out":
        amount = amount * -1
    else:
        pass
    #Input all information into the Class
    transaction = Transaction(transaction_id=transaction_id,transaction_name=transaction_name,date=date,pot=pot,vault=vault,type=transaction_type,amount=amount,user=user)
    transaction_data = [(transaction_id,transaction_name,date,pot.pot_id,vault.vault_id,transaction_type,amount,username)]
    if transaction:
        print_slow_nospace("\nThanks, your transaction has been created succesfully")
        # Save transaction to database
        cur = con.cursor()
        cur.executemany("INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?)",transaction_data)
        con.commit()
        cur.close()
    else:
        print_slow("ERROR: transaction not created succesfully")
    return transaction

def transfer_transaction(con,x,pot,vault,user,transaction_name,date,transaction_type,amount):
    transaction_id = x
    # Collect transaction amount
    print_slow(f"\nForecasted transaction amount was ${amount}. Is this correct? (Y/N)")
    while True:
        amount_query = input()
        if amount_query == "Y":
            break
        elif amount_query == "N":
            print_slow("\nWhat is the transaction amount?: ")
            while True:
                amount = int_validator()
                if amount > 0:
                    break
                else:
                    print_slow("\namount must be greater than 0")
            break
        else:
            continue

    #Input all information into the Class
    transaction = Transaction(transaction_id=transaction_id,transaction_name=transaction_name,date=date,pot=pot,vault=vault,type=transaction_type,amount=amount,user=user)
    transaction_data = [(transaction_id,transaction_name,date,pot.pot_id,vault.vault_id,transaction_type,amount,user.username)]
    if transaction:
        print_slow("\nThanks, your transaction has been transferred succesfully")
        # Save transaction to database
        cur = con.cursor()
        cur.executemany("INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?)",transaction_data)
        con.commit()
        cur.close()
    else:
        print_slow("ERROR: transaction not transferred succesfully")
    return transaction

def print_slow(txt):
    for x in txt: 
        print(x,end='',flush=True)
        sleep(0) #0.025 for slow text
    print()
    print()

def print_slow_nospace(txt):
    for x in txt: 
        print(x,end='',flush=True)
        sleep(0) #0.025 for slow text
    print()

def int_validator():
    while True:
        try:
            value = int(input())
            break
        except ValueError:
            print_slow("\nInvalid input. Please enter a valid integer: ")
    return value

def collect_date(message):
    while True:
        try:
            print_slow(message) 
            date_input = input().strip()
            date = datetime.datetime.strptime(date_input,"%d/%m/%y")
            return date 
        except ValueError as err:
            print_slow_nospace(f"\nInvalid date: {err}. Please use DD/MM/YY format\n")

def convert_date(string):
    try:
        date_input = string
        date = datetime.datetime.strptime(date_input,"%Y-%m-%d %H:%M:%S")
    except ValueError as err:
        print_slow(err)
    return date

def forecast_balance_vault(selected_vault,pots,smallest_date,delta_weeks):
    date_list = [smallest_date + datetime.timedelta(days=7*i) for i in range(delta_weeks + 1)]
    table_rows = []
    for week_num,date in enumerate(date_list,start=1):
        # Start with current vault value (base + transactions)
        vault_total = selected_vault.vault_value()
        # Add only future forecasts for each pot
        for pot in pots.values():
            if pot.vault_id == selected_vault.vault_id:
                vault_total += pot.pot_forecast_value(date)
        table_rows.append((week_num,date,vault_total))
    return print(f"\n{tabulate(table_rows,headers=["Week No.","Date","Balance"],tablefmt="heavy_grid")}\n")

def forecast_balance_pot(selected_pot,pots,smallest_date,delta_weeks):
    date_list = [smallest_date + datetime.timedelta(days=7*i) for i in range(delta_weeks + 1)]
    table_rows = []
    for week_num,date in enumerate(date_list,start=1):
        # Start with current vault value (base + transactions)
        pot_total = selected_pot.pot_value()
        # Add only future forecasts for each pot
        for pot in pots.values():
            if pot.pot_id == selected_pot.pot_id:
                pot_total += pot.pot_forecast_value(date)
        table_rows.append((week_num,date,pot_total))
    return print(f"\n{tabulate(table_rows,headers=["Week No.","Date","Balance"],tablefmt="heavy_grid")}\n")
        
def summary(vaults,pots):
    print()
    for i in vaults:
        vault = vaults[i]
        # Pot data
        pot_rows = []
        for j in pots:
            if pots[j].vault == vault:
                pot_value = pots[j].pot_value()
                pot_rows.append([pots[j].pot_name,f"${pot_value}"])

        vault_value = vault.vault_value()
        title_row = [f"Vault Name: {vault.vault_name}",f"Vault Value: ${vault_value}"]
        header_row = ["Pot Names","Pot Values"]
        # Combine into one table
        full_table = [title_row,header_row] + pot_rows
        print(tabulate(full_table,tablefmt="heavy_grid"),end="\n\n")

def transaction_summary(transactions): 
    table = []
    for i in transactions:
        row = [transactions[i].transaction_id,transactions[i].transaction_name,transactions[i].date,transactions[i].amount]
        table.append(row)

    print(f"\n{tabulate(table,headers=["transaction_id","transaction_name","date","amount"],tablefmt="heavy_grid")}\n")
    
def forecast_summary(forecasts): 
    table = []
    for forecast in forecasts.values():
        row = [forecast.forecast_id,forecast.forecast_name,forecast.date,forecast.amount]
        table.append(row)

    print(f"\n{tabulate(table,headers=["forecast_id","forecast_name","date","amount"],tablefmt="heavy_grid")}\n")

def create_user(con,*args):
    cur = con.cursor()
    if args:
        username = args[0]
        user = User(username)
    else:
        print_slow("Now firstly, what is your name?: ")
        username = input()
        user = User(username)

    cur.execute("INSERT INTO users VALUES(?)",(user.username,))
    con.commit()
    cur.close()
    return user

def create_pot(con,x,vault,user,username):
    cur = con.cursor()
    print_slow("\nWhat is your preferred name for the pot?: ")
    pot_name = input()
    pot_id = x + 1
    print_slow("\nWhat is the amount of money in the pot?: ")
    while True:
        amount = int_validator()
        if amount > 0:
            break
        else:
            print_slow("\namount must be greater than 0") 

    #Input all information into the Class
    pot = Pot(pot_id=pot_id,pot_name=pot_name,vault=vault,amount=amount,user=user)
    if pot:
        print_slow("\nThanks, your pot has been created succesfully")
        # save pot to database
        pots_data = []
        pots_data.append((pot.pot_id,pot.pot_name,pot.vault_id,pot.amount,username))
        cur.executemany("INSERT INTO pots VALUES(?,?,?,?,?)",pots_data)
        con.commit()
        con.close()
    else:
        print_slow("\nERROR: pot not created succesfully")
    return pot

def create_vault(con,x,user,username):
    cur = con.cursor()
    print_slow("\nWhat is your preferred name for the vault?: ")
    vault_name = input()
    vault_id = x + 1    
    #Input all information into the Class
    vault = Vault(vault_id=vault_id,vault_name=vault_name,user=user)
    if vault:
        print_slow("\nThanks, your vault has been created succesfully")
        # save vault to database
        vaults_data = []
        vaults_data.append((vault.vault_id,vault.vault_name,username))
        cur.executemany("INSERT INTO vaults VALUES(?,?,?)",vaults_data)
        con.commit()
        cur.close()
    else:
        print_slow("ERROR: vault not created succesfully")
    return vault

def create_profile(con):
    # Create a User object
    user = create_user(con)
    # Count number of existing vaults in database. if not exist = 0
    start_vault = count_vaults()
    if start_vault == None:
        start_vault = 0
    # Count number of existing pots in database. if not exist = 0
    start_pot = count_pots()
    if start_pot == None:
        start_pot = 0
    # Create a Vault object with valid data
    print_slow(f"\nHi {user.username}, let me help you create some vaults. How many do you want to create?: ")
    no_vaults = int_validator()
    vaults = {}
    
    try:
        for x in range(no_vaults):
            vaults["vault_{0}".format((x+1)+start_vault)] = create_vault((x+start_vault),user)
    except ValueError as e:  
        print_slow(f"\nError: {e}")
    except Exception as e:  
        print_slow(f"\nAn unexpected error occurred: {e}")

    # Create Pot objects with valid data
    print_slow("Now, let me help you create some pots. How many do you want to create?: ")
    no_pots = int_validator()
    pots = {}
    
    while True:
        try:
            for x in range(no_pots):
                while True: 
                    print_slow("\nWhat vault should this pot be assigned to?: ")
                    vault_input = input()
                    # Find the vault using a simple loop
                    selected_vault = None
                    for vault in vaults.values():
                        if vault.vault_name == vault_input and vault.username == user.username:
                            selected_vault = vault
                            break
                    if selected_vault:
                        pots[f"pot_{(x+1)+start_pot}"] = create_pot((x+start_pot),selected_vault,user)
                        break
                    else:
                        print_slow(f"Vault '{vault_input}' not found. Please enter a valid vault name.")        
            break
        
        except ValueError as e:  
            print_slow(f"Error: {e}")

        except Exception as e:  
            print_slow(f"An unexpected error occurred: {e}")

    # Summary of the vaults and pots values
    print_slow("See below list of vaults and their summed values")
    summary(vaults,pots)

    return user,vaults,pots

def instructions():
    return """In this program, your savings are organized into two categories: vaults and pots.

- A vault is a collection of Pots
- A pot represents an individual budget within a Vault

For example, you might create a 'Travelling' vault
to manage your holiday expenses. This vault could contain multiple pots, each
representing a budget for a different destination. Attached to the pots can be either 
"transactions" or "forecasts" to represent actual or predicted expenditure, thus creating 
a financal management model. 

Once you've set up your vaults and pots, the program will enter an infinite loop
where you can choose from the following options:

1. "New" to submit a new item (profile, vaults, pots, transactions, forecasts),
2. "Summary" to get either a balance report, forecast report or transactions summary,
3. "Delete" to remove an item,
4. "Instructions" to get further information on how to use Money Pots,
5. "Exit" to terminate the programme

The data collected is stored in an SQL database. The user can log back in when the programme
is re-executed to start where they left off. 

We hope you enjoy using Money Pots!"""

def re_user(con,name):
    cur = con.cursor()
    # Searcb the users database for all information for defined user 
    res = cur.execute("SELECT * FROM users WHERE username = ?",(name,))
    returned_user = res.fetchall()
    # Create variable
    username = returned_user[0]
    # Create user instance
    user = User(username=username)
    cur.close()
    return user

def re_vaults(con,name,user):
    cur = con.cursor()
    # Create vault and vault_ids variables
    vaults = {}
    vault_ids = []
    # Searcb the vaults database for all information for defined user 
    res = cur.execute("SELECT * FROM vaults WHERE username = ?",(name,))
    returned_vaults = res.fetchall()
    for vault in returned_vaults:
        # Create variables
        vault_ids.append(int(vault[0]))
        vault_id = int(vault[0])
        vault_name = vault[1]
        # Create vault instance
        vault = Vault(vault_id=vault_id,vault_name=vault_name,user=user)
        # Add instance to vaults object dictionary
        vaults["vault_{0}".format(vault_id)] = vault
    cur.close()
    return vaults,vault_ids

def re_pots(con,vaults,vault_ids,user):
    cur = con.cursor()
    # Create pots and pot_id variables
    pots = {}
    pot_ids = []
    # Searcb the vaults database for all information for defined vault_ids
    for vault in vault_ids:
        res = cur.execute("SELECT * FROM pots WHERE vault_id = ?",(vault,))
        returned_pots = res.fetchall()
        for pot in returned_pots:
            # Create variables
            pot_id = int(pot[0])
            pot_name = pot[1]
            amount = int(pot[3])
            vault = vaults[f"vault_{pot[2]}"] 
            # Create pot instance
            pot = Pot(pot_id=pot_id,pot_name=pot_name,vault=vault,amount=amount,user=user)
            # Add instance to pots object dictionary
            pots[f"pot_{pot.pot_id}"] = pot
            # Append pot_id to list
            pot_ids.append(pot_id)

    cur.close()
    return pots,pot_ids

def re_forecasts(con,pots,vaults,pot_ids,user):
    cur = con.cursor()
    # Create forecasts and forecast_id variables
    forecasts = {}
    forecast_ids = []
    # Searcb the pots database for all information for defined pot_ids
    for pot in pot_ids:
        res = cur.execute("SELECT * FROM forecasts WHERE pot_id = ?",(pot,))
        returned_forecasts = res.fetchall()
        for forecast in returned_forecasts:
            # Create variables
                forecast_id = int(forecast[0])
                forecast_name = forecast[1]
                date = convert_date(forecast[2])
                type = (forecast[5])
                amount = int(forecast[6])
                pot = pots[f"pot_{forecast[3]}"] 
                vault = vaults[f"vault_{forecast[4]}"] 
                # Create forecast instance
                forecast = Forecast(forecast_id=forecast_id,forecast_name=forecast_name,date=date,pot=pot,vault=vault,type=type,amount=amount,user=user)
                # Add instance to transactions object dictionary
                forecasts[f"forecast_{forecast.forecast_id}"] = forecast
                # Append transaction_id to list
                forecast_ids.append(forecast_id)
    cur.close()
    return forecasts,forecast_ids

def re_transactions(con,pots,vaults,pot_ids,user):
    cur = con.cursor()
    # Create transaction_id variables
    transactions = {}
    transaction_ids = []
    # Searcb the pots database for all information for defined pot_ids
    for pot in pot_ids:
        res = cur.execute("SELECT * FROM transactions WHERE pot_id = ?",(pot,))
        returned_transactions = res.fetchall()

        for transaction in returned_transactions:
            # Create variables
                transaction_id = int(transaction[0])
                transaction_name = transaction[1]
                date = convert_date(transaction[2])
                type = (transaction[5])
                amount = int(transaction[6])
                pot = pots[f"pot_{transaction[3]}"] # Dictionary key format is "Pot_1: Object"
                vault = vaults[f"vault_{transaction[4]}"] # Dictionary key format is "Vault_1: Object"
                # Create transaction instance
                transaction = Transaction(transaction_id=transaction_id,transaction_name=transaction_name,date=date,pot=pot,vault=vault,type=type,amount=amount,user=user)
                # Add instance to transactions object dictionary
                transactions[f"transaction_{transaction.transaction_id}"] = transaction
                # Append transaction_id to list
                transaction_ids.append(transaction_id)

    cur.close()
    return transactions,transaction_ids

def count_pots(con):
    cur = con.cursor()
    res = cur.execute("""
        SELECT pot_id 
        FROM pots 
        ORDER BY pot_id DESC 
        LIMIT 1;
    """)
    highest_pot = res.fetchone() 
    cur.close()
    return highest_pot[0] if highest_pot else None
        
def count_vaults(con):
    cur = con.cursor()
    res = cur.execute("""
        SELECT vault_id
        FROM vaults
        ORDER BY vault_id DESC
        LIMIT 1;             
    """)
    highest_vault = res.fetchone() 
    cur.close()
    return highest_vault[0] if highest_vault else None
        
def count_transactions(con):
    cur = con.cursor()
    res = cur.execute("""
        SELECT transaction_id 
        FROM transactions
        ORDER BY transaction_id DESC 
        LIMIT 1;
    """)
    highest_transaction = res.fetchone()  
    cur.close()
    return highest_transaction[0] if highest_transaction else None

def count_forecasts(con):
    cur = con.cursor()
    res = cur.execute("""
        SELECT forecast_id 
        FROM forecasts 
        ORDER BY forecast_id DESC 
        LIMIT 1;
    """)
    
    highest_forecast = res.fetchone()  # Use fetchone() since we only expect one result
    cur.close()
    return highest_forecast[0] if highest_forecast else None
    
    highest_forecast = res.fetchone()  # Use fetchone() since we only expect one result
    cur.close()
    return highest_forecast[0] if highest_forecast else None

def del_profile(con,user,username):
    try:
        # Delete all related data first
        cur = con.cursor()
        cur.execute("DELETE FROM transactions WHERE username = ?",(username,))
        cur.execute("DELETE FROM pots WHERE username = ?",(username,))
        cur.execute("DELETE FROM vaults WHERE username = ?",(username,))
        # Finally,delete the user
        cur.execute("DELETE FROM users WHERE username = ?",(username,))
        con.commit()
        cur.close()
        print_slow_nospace("\nProfile deleted successfully.")

    except sqlite3.Error as e:
        print_slow(f"\nError deleting profile: {e}")

def del_vault(con,user,vaults,username):
    vault_name = input("\nEnter the name of the Vault you want to delete: \n\n").strip()
    # Search for the vault that matches both the name and the username
    selected_vault = None
    for vault in vaults.values():
        if vault.vault_name == vault_name and vault.username[0] == username:
            selected_vault = vault
            break

    if selected_vault:
        vault_id = selected_vault.vault_id
        # Proceed with deletion of related data first
        cur = con.cursor()
        cur.execute("DELETE FROM transactions WHERE vault_id = ?",(vault_id,))
        cur.execute("DELETE FROM pots WHERE vault_id = ?",(vault_id,))
        # Finally delete the vault
        cur.execute("DELETE FROM vaults WHERE vault_id = ?",(vault_id,))
        con.commit()
        cur.close()
        print_slow_nospace("\nVault deleted succesfully")
        return True

    else:
        print_slow(f"\nVault '{vault_name}' not found for user '{username}'.")
        print_slow_nospace(f"Available vaults for {username}: {[v.vault_name for v in vaults.values() if v.username[0] == username]}\n")
        return False

def del_pot(con,user,pots,username):
    pot_name = input("\nEnter the name of the Pot you want to delete: \n\n").strip()
    # Search for the pot that matches both the name and the username
    selected_pot = None
    for pot in pots.values():
        if pot.pot_name == pot_name and pot.username[0] == username:
            selected_pot = pot
            break

    if selected_pot:
        pot_id = selected_pot.pot_id
        # Proceed with deletion of related data first
        cur = con.cursor()
        cur.execute("DELETE FROM transactions WHERE pot_id = ?",(pot_id,))
        # Finally delete the pot
        cur.execute("DELETE FROM pots WHERE pot_id = ?",(pot_id,))
        con.commit()
        cur.close()
        print_slow_nospace("\nPot deleted succesfully")
        return True

    else:
        print_slow(f"\nPot '{pot_name}' not found for user '{username}'.")
        print_slow_nospace(f"Available pots for {username}: {[p.pot_name for p in pots.values() if p.username[0] == username]}")
        return False

def del_transaction(con,user,transactions,username):
    try:
        transaction_id = int(input("\nEnter the transaction_id that you want to delete: \n\n").strip())
    except ValueError:
        print_slow("\nInvalid transaction ID. Must be a number.")
        return False
    # Search for the transaction that matches both the id and the username
    selected_transaction = None
    for transaction in transactions.values():
        if transaction.transaction_id == transaction_id and transaction.username[0] == username:
            selected_transaction = transaction
            break
    if selected_transaction:
        # Delete the transaction
        cur = con.cursor()
        cur.execute("DELETE FROM transactions WHERE transaction_id = ?",(transaction_id,))
        con.commit()
        cur.close()
        print_slow_nospace("\nTransaction deleted succesfully")
        return True
    else:
        print_slow(f"\nTransaction '{transaction_id}' not found for user '{username}'.")
        print_slow_nospace(f"Available transactions for {username}: {[t.transaction_id for t in transactions.values() if t.username[0] == username]}")
        return False

def del_forecast(con,user,forecasts,forecast_id,username):
    cur = con.cursor()
    # Search for the transaction that matches both the id and the username
    selected_forecast = None
    for forecast in forecasts.values():
        if forecast.forecast_id == forecast_id and forecast.username[0] == username:
            selected_forecast = forecast
            break
    if selected_forecast:
        # Delete the forecast
        cur.execute("DELETE FROM forecasts WHERE forecast_id = ?",(forecast_id,))
        con.commit()
        cur.close()
        print_slow_nospace("\nForecast deleted succesfully")
        return True
    else:
        print_slow(f"\nForecast '{forecast_id}' not found for user '{username}'.")
        print_slow_nospace(f"Available transactions for {username}: {[t.transaction_id for t in transactions.values() if t.username[0] == username]}")
        return False

def user_exist(con,login):
    user_exists = False
    # SQL query to determine if user exists
    cur = con.cursor()
    res = cur.execute("SELECT username FROM users")
    returned_users = res.fetchall()
    cur.close()
    for user in returned_users:
        if login == user[0]:
            user_exists = True
            return user_exists
        else:
            return user_exists

def refresh_user_data(con,user,username):
    cur = con.cursor()
    #reinstantiate vaults
    vaults,vault_ids = re_vaults(con,username,user)
    #reinstantiate pots
    pots,pot_ids = re_pots(con,vaults,vault_ids,user)
    #reinstantiate transactions
    res = cur.execute("SELECT * FROM transactions")
    transaction_exists = bool(res.fetchall())
    transactions, transaction_ids = re_transactions(con,pots,vaults,pot_ids,user) if transaction_exists else ({}, [])
    #reinstantiate forecasts
    res = cur.execute("SELECT * FROM forecasts")
    forecast_exists = bool(res.fetchall())
    forecasts,forecast_ids = re_forecasts(con,pots,vaults,pot_ids,user) if forecast_exists else ({}, [])
    # Query forecasts to see if any of these are now in the past. Store in past_forecasts variable
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    res = cur.execute("SELECT * FROM forecasts WHERE date < ?",(today,))
    past_forecasts = res.fetchall()
    len_past_forecasts = len(past_forecasts)

    if len_past_forecasts > 0:
        print_slow("\nYou have forecasted expenditure, which now needs to be confirmed. Please see below:")
        # Submit these forecasts as transactions
        start_transaction = count_transactions(con)
        for forecast in past_forecasts:
            counter = 1
            date = convert_date(forecast[2])
            selected_pot = None
            selected_vault = None
            for pot in pots.values():
                if pot.pot_id == forecast[3] and pot.username == user.username: 
                    selected_pot = pot
                    selected_vault = vaults.get(f"vault_{pot.vault_id}")
                    break
            BOLD_RED = "\033[1;31m"
            RESET = "\033[0m"
            print_slow_nospace(f"{BOLD_RED}Forecast_ID:{RESET} {forecast[0]}{BOLD_RED} Forecast Name:{RESET} {forecast[1]}")
            transfer_transaction(con,(start_transaction + counter),selected_pot,selected_vault,user,forecast[1],date,forecast[5],forecast[6])
            counter += 1
        # Delete these forecasts from the database
        for forecast in past_forecasts:
            success = del_forecast(con,user,forecasts,forecast[0],username)
            if success:
                #reinstantiate forecasts
                forecast_exists = False
                res = cur.execute("SELECT * FROM forecasts")
                returned_forecasts = res.fetchall()
                if len(returned_forecasts) > 0:
                    forecast_exists = True
                if forecast_exists == False:
                    forecasts = {}
                    forecast_ids = []
                else:
                    forecasts,forecast_ids = re_forecasts(con,pots,vaults,pot_ids,user)
                break
            else:
                continue

    cur.close()
    return vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids
