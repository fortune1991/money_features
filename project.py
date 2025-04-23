import datetime, os, sqlite3, math
from project_classes import User, Vault, Pot, Transaction
from project_functions import submit_forecast, transfer_transaction, submit_transaction, print_slow, print_slow_nospace, int_validator, collect_date, convert_date, summary, create_pot, create_user, create_vault, create_profile, instructions, re_user, re_vaults, re_pots, re_transactions, re_forecasts, count_pots, count_transactions, count_vaults, count_forecasts, transaction_summary, forecast_summary, del_profile, del_vault, del_pot, del_transaction, del_forecast, forecast_balance_vault, forecast_balance_pot
from tabulate import tabulate
from time import sleep
from database import create_database

import warnings
warnings.filterwarnings("ignore", message="The default datetime adapter is deprecated", category=DeprecationWarning)

def main():
    vaults = {}
    pots = {}
    transactions = {}
    forecasts = {}
    
    database_exists = os.path.isfile("/Users/michaelfortune/Developer/projects/money/money_features/money.db")
    
    if not database_exists:

        create_database()
        print_slow("""
Welcome to Money Pots, your savings and budgeting calculator.""")
        print_slow(instructions())
        
        user, vaults, pots = create_profile()

        username = user.username
    
    if database_exists:
        #log user in
        while True:
            # Establish a connection to the Database
            db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db" 
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            print_slow("""
Welcome to Money Pots, your savings and budgeting calculator. Let me help you to login and view your profile. What's your username?""")
            login = input().strip() # Remove trailing white space
            user_exists = False

            # SQL query to determine if user exists

            res = cur.execute("SELECT username FROM users")
            returned_users = res.fetchall()
            for user in returned_users:
                if login == user[0]:
                    user_exists = True
            
           # if user exists, reinstantiate objects from the database
                        
            if user_exists == True:
                print()
                print_slow("Welcome back to Money Pots")
                #reinstantiate user
                user = re_user(login)
                username = user.username 
                #reinstantiate vaults 
                vaults, vault_ids = re_vaults(login, user)
                #reinstantiate pots
                pots, pot_ids = re_pots(vaults, vault_ids, user)
                #reinstantiate transactions 
                transaction_exists = False
                res = cur.execute("SELECT * FROM transactions")
                returned_transactions = res.fetchall()
                if len(returned_transactions) > 0:
                    transaction_exists = True
                if transaction_exists == False:
                    pass
                else:
                    transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)
                #reinstantiate forecasts
                forecast_exists = False
                res = cur.execute("SELECT * FROM forecasts")
                returned_forecasts = res.fetchall()
                if len(returned_forecasts) > 0:
                    forecast_exists = True
                if forecast_exists == False:
                    pass
                else:
                    forecasts, forecast_ids = re_forecasts(pots, vaults, pot_ids, user)

                # Query forecasts to see if any of these are now in the past. Store in past_forecasts variable
                today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                
                res = cur.execute("SELECT * FROM forecasts WHERE date < ?", (today,))
                past_forecasts = res.fetchall()
                len_past_forecasts = len(past_forecasts)

                if len_past_forecasts > 0:
                    print_slow("\nYou have forecasted expenditure, which now needs to be confirmed. Please see below:")
                    
                    # Submit these forecasts as transactions
                    start_transaction = count_transactions()
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
                        
                        transfer_transaction((start_transaction + counter), selected_pot, selected_vault, user, forecast[1], date, forecast[5], forecast[6])
                        counter += 1

                    # Delete these forecasts from the database
                    for forecast in past_forecasts:
                        success = del_forecast(user,forecasts,forecast[0])

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
                                forecasts, forecast_ids = re_forecasts(pots, vaults, pot_ids, user)

                            break
                        else:
                            continue

                # Update Pots and Vaults values, using class methods

                for pot in pots.values():
                    pot.pot_value()
                
                for vault in vaults.values():
                    vault.vault_value()

                break

            else:
                print_slow("\nUser doesn't exist. Respond 'Try again' 'New user' or 'Exit'")    
                response = input()

                if response == "New user":
                    print_slow("\nExcellent. Please answer the following questions to create a new user profile")
                    user, vaults, pots = create_profile()
                    break
                elif response == "Try again":
                    continue
                elif response == "Exit":
                    exit()
                else:
                    print_slow_nospace("\nUnknown Command. Please try to login again")                
     
# Loop Menu on Command line until exit

    # Establish DB Connection
    db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db" 
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    while True:
        print_slow('\033[1;31mMain Menu\033[0m\n\nNow, I await your commands to proceed. Please type: \n\n"New" to submit a new item (profile, vaults, pots, transactions, forecasts), \n"Summary" to get either a balance report, forecast report or transactions summary, \n"Delete" to remove an item, \n"Instructions" to get further information on how to use Money Pots, \n"Exit" to terminate the programme')
        action = input()
        if action == "New":
            while True:
                print_slow('\nWhat type of new item would you like to create? \n\n\033[1;31mNew Items Menu\033[0m \n\n"Profile" to create a new user profile, \n"Vault" to create a new vault, \n"Pot" to create a new pot, \n"Transaction" to submit a new transaction, \n"Forecast" to submit an estimate for predicted spending, \n"Exit" to return back to main menu')
                new_action = input()

                if new_action == "Profile":
                    print_slow("\nExcellent. Please answer the following questions to create a new user profile")
                    transactions= {}
                    forecasts = {}
                    user, vaults, pots = create_profile()
                    break

                elif new_action == "Vault":
                    vault_count = count_vaults()
                    vaults[f"vault_{(vault_count + 1)}"] = create_vault(vault_count, user)
                    
                    # Create associated pots
                    print_slow_nospace("Now, let's create at least one pot to associate with this vault")
                    pot_count = count_pots()
                    selected_vault = vaults.get(f"vault_{(vault_count + 1)}")

                    pots[f"pot_{(pot_count + 1)}"] = create_pot(pot_count, selected_vault, user)

                    action = ""
                    break

                elif new_action == "Pot":
                    while True:
                        try:
                            print_slow("\nWhat vault will this pot be assigned to? ")
                            pot_vault = input()
                            pot_count = count_pots()
                            selected_vault = None
                            for vault in vaults.values():
                                if vault.vault_name == pot_vault and vault.username == user.username:
                                    selected_vault = vault

                            if selected_vault:
                                pots[f"pot_{(pot_count + 1)}"] = create_pot(pot_count, selected_vault, user)

                                break

                            else:
                                print_slow(f"Vault '{vault_input}' not found. Please enter a valid vault name.")
                                
                        except ValueError as e:  
                            print_slow(f"Error: {e}")
                            print_slow("Please try again")
                            
                        except Exception as e:  
                            print_slow(f"An unexpected error occurred: {e}")
                            print_slow("Please try again")
                        break
                    action = ""
                    break

                elif new_action == "Transaction":
                    print_slow("\nExcellent. Now, let me help you create a new transaction.")
                    while True:
                        try:
                            while True: 
                                # Count existing transactions
                                start_transaction = count_transactions()
                                if start_transaction == None:
                                    start_transaction = 0
                                
                                print_slow("What pot should this pot be assigned to?: ")
                                pot_input = input()

                                # Find the pot using a simple loop
                                selected_pot = None
                                selected_vault = None
                                for pot in pots.values():
                                    if pot.pot_name == pot_input and pot.username == user.username: 
                                        selected_pot = pot
                                        selected_vault = vaults.get(f"vault_{pot.vault_id}")
                                        break

                                if selected_pot:
                                    transactions[f"transaction_{1}"] = submit_transaction(start_transaction, selected_pot, selected_vault, user)
                                    selected_pot.pot_value()
                                    break
                                else:
                                    print_slow(f"pot '{pot_input}' not found. Please enter a valid pot name.")
                            
                            break
                        
                        except ValueError as e:  
                            print_slow(f"Error: {e}")
                            
                        except Exception as e:  
                            print_slow(f"An unexpected error occurred: {e}")
                            
                        break
                    
                elif new_action == "Forecast":
                    while True:
                        print_slow('\nOK, would you like to submit a "Single expense" or a "Weekly expense"? or "Exit" to return back to the main menu')
                        expense = input()

                        if expense == "Single expense":
                            # Collect forecast name
                            print_slow("\nPlease provide a name reference for this Forecast: ")
                            forecast_name = input()
                            while True:
                                single = int(input("\nWhat's the amount of your predicted expenditure? \n\n"))
                                if single > 0:
                                    break
                                else:
                                    print_slow("\namount must be greater than 0")

                            # Collect forecast type
                            while True:
                                types = ["in", "out"]
                                print_slow('\nPlease define the type of forecast. "in" or "out": ')
                                forecast_type = input()
                                if forecast_type not in types:
                                    print_slow("\nincorrect forecast reference")
                                else:
                                    break
                                
                            if forecast_type == "out":
                                single = single * -1
                            else:
                                pass
                        
                            print_slow("\nExcellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
                            
                            while True:
                                expense_date = collect_date("Date of transaction: ")
                                today = datetime.datetime.today()
                                if expense_date < today:
                                    print_slow("\nInvalid Date, must be in the future for a forecast")
                                else:
                                    break

                            try:
                                while True: 
                                    # Count existing forecasts
                                    start_forecast = count_forecasts()
                                    if start_forecast == None:
                                        start_forecast = 0
                                    print_slow("\nWhat pot should this pot be assigned to?: ")
                                    pot_input = input()

                                    # Find the pot using a simple loop
                                    selected_pot = None
                                    selected_vault = None
                                    for pot in pots.values():
                                        if pot.pot_name == pot_input and pot.username == user.username: 
                                            selected_pot = pot
                                            selected_vault = vaults.get(f"vault_{pot.vault_id}")
                                            break

                                    if selected_pot:
                                        forecasts[f"forecast_{1}"] = submit_forecast(forecast_name, start_forecast, selected_pot, selected_vault, user, expense_date, single, forecast_type)
                                        selected_pot.pot_value()
                                        break
                                    else:
                                        print_slow(f"pot '{pot_input}' not found. Please enter a valid pot name.")
                                        
                            
                            except ValueError as e:  
                                print_slow(f"Error: {e}")
                                
                            except Exception as e:  
                                print_slow(f"An unexpected error occurred: {e}")
                            
                            
                        elif expense == "Weekly expense":
                            # Collect forecast name
                            print_slow("\nPlease provide a name reference for this Forecast: ")
                            forecast_name = input()

                            while True:
                                weekly = int(input("\nWhat's your predicted weekly expenditure? "))
                                if weekly > 0:
                                    break
                                else:
                                    print_slow("\nAmount must be greater than 0")

                            # Collect forecast type
                            while True:
                                types = ["in", "out"]
                                print_slow('\nPlease define the type of forecast. "in" or "out": ')
                                forecast_type = input()
                                if forecast_type not in types:
                                    print_slow("\nincorrect forecast reference")
                                else:
                                    break
                                
                            if forecast_type == "out":
                                weekly = weekly * -1
                            else:
                                pass

                            no_weeks = int(input("\nHow many weeks is this for? "))
                            print_slow("\nExcellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
                            
                            while True:
                                expense_date = collect_date("Date of transaction: ")
                                today = datetime.datetime.today()
                                date_list = {}
                                if expense_date < today:
                                    print_slow("\nInvalid Date, must be in the future for a forecast")
                                else:
                                    for i in range (0, no_weeks, 1):
                                        date = expense_date + datetime.timedelta(days=(7*i))
                                        date_list[i] = date
                                    break

                            try:
                                while True: 
                                    start_forecast = count_forecasts()
                                    if start_forecast == None:
                                        start_forecast = 0
                                    print_slow("\nWhat pot should this pot be assigned to?: ")
                                    pot_input = input()

                                    # Find the pot using a simple loop
                                    selected_pot = None
                                    selected_vault = None
                                    for pot in pots.values():
                                        if pot.pot_name == pot_input and pot.username == user.username: 
                                            selected_pot = pot
                                            selected_vault = vaults.get(f"vault_{pot.vault_id}")
                                            break

                                    if selected_pot:
                                        for key, date in date_list.items():
                                            forecasts[f"forecast_{key}"] = submit_forecast(forecast_name, (start_forecast + key), selected_pot, selected_vault, user, date, weekly, forecast_type)
                                            selected_pot.pot_value()
                                        break
                                    else:
                                        print_slow(f"pot '{pot_input}' not found. Please enter a valid pot name.")
                                        
                            
                            except ValueError as e:  
                                print_slow(f"Error: {e}")
                                
                            except Exception as e:  
                                print_slow(f"An unexpected error occurred: {e}")
                            
                        elif expense == "Exit":
                            print()
                            break
                            
                        else:
                            print_slow("\nPlease enter a valid expense type ('Single expense', 'Weekly expense', or 'Exit' to return")
                        
                        break

                elif new_action == "Exit":
                    action = ""
                    print()
                    break

                else:
                    print_slow("\nSorry, I don't recognize that instruction. Please try again.")

                action = ""
                break

        if action == "Summary":
            while True:
                print_slow('\n\033[1;31mSummary Menu\033[0m\n\nWhat type of summary would you like to create? \n\n"Current Balance Report" to show your vaults and pots balances today, \n"Forecast Balance Report" to show your vaults or pots balances from a given start date until the final forecast estimate, \n"Forecast List" to show a list of your predicted forecast expenditures, \n"Transaction list" to show a list of all your recorded transactions, \n"Exit" to return back to the main menu')
                summary_action = input()

                if summary_action == "Current Balance Report":
                    #reinstantiate vaults 
                    vaults, vault_ids = re_vaults(username, user)
                    #reinstantiate pots
                    pots, pot_ids = re_pots(vaults, vault_ids, user)
                    #reinstantiate transactions 
                    transaction_exists = False
                    res = cur.execute("SELECT * FROM transactions")
                    returned_transactions = res.fetchall()
                    if len(returned_transactions) > 0:
                        transaction_exists = True

                    if transaction_exists == False:
                        transactions = {}
                        transaction_ids = []

                    else:
                        transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                    #create balance summary
                    summary(vaults, pots)
                    break

                if summary_action == "Forecast Balance Report":
                    #reinstantiate vaults 
                    vaults, vault_ids = re_vaults(username, user)
                    #reinstantiate pots
                    pots, pot_ids = re_pots(vaults, vault_ids, user)
                    #reinstantiate transactions 
                    transaction_exists = False
                    res = cur.execute("SELECT * FROM transactions")
                    returned_transactions = res.fetchall()
                    if len(returned_transactions) > 0:
                        transaction_exists = True

                    if transaction_exists == False:
                        transactions = {}
                        transaction_ids = []

                    else:
                        transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)
                    
                    #reinstantiate forecasts
                    forecast_exists = False
                    res = cur.execute("SELECT * FROM forecasts")
                    returned_forecasts = res.fetchall()
                    if len(returned_forecasts) > 0:
                        forecast_exists = True
                    if forecast_exists == False:
                        pass
                    else:
                        forecasts, forecast_ids = re_forecasts(pots, vaults, pot_ids, user)

                    while True:
                        print_slow('\nWould you like to forecast the balance for a "Vault" or "Pot"?')
                        option = input()

                        if option == "Vault":
                            print_slow("\nWhat is the name of the Vault you would like to forecast?")
                            name = input()
                            selected_vault = None
                            for vault in vaults.values():
                                if vault.vault_name == name and vault.username == user.username:
                                    selected_vault = vault
                            
                            #Get list of forecasts linked to this vault                            
                            res = cur.execute("SELECT * FROM forecasts WHERE vault_id = ?", (selected_vault.vault_id,))
                            vault_forecasts = res.fetchall()
                            
                            #Find 'smallest' date
                            print_slow("\nWhat date would you like to start the forecast from?")
                            smallest_date = collect_date("Date: ")
                            
                            #Find 'biggest' date
                            try: 
                                biggest_date = vault_forecasts[0][2]
                            except IndexError as e:  
                                print_slow(f"\nError: {e}")
                                print_slow("No forecasts recorded for this Vault")
                                break

                            for forecast in vault_forecasts:
                                if forecast[2] > biggest_date:
                                    biggest_date = forecast[2]
                                else:
                                    continue
                            biggest_date = convert_date(biggest_date)

                            delta = biggest_date - smallest_date
                            delta_days = delta.days
                            delta_weeks = math.ceil(delta_days / 7)
                            
                            forecast_balance_vault(selected_vault, pots, smallest_date, delta_weeks)
                            break

                        elif option == "Pot":
                            print_slow("\nWhat is the name of the Pot you would like to forecast?")
                            name = input()
                            selected_pot = None
                            for pot in pots.values():
                                if pot.pot_name == name and pot.username == user.username:
                                    selected_pot = pot
                            
                            #Get list of forecasts linked to this pot                           
                            res = cur.execute("SELECT * FROM forecasts WHERE pot_id = ?", (selected_pot.pot_id,))
                            pot_forecasts = res.fetchall()
                            
                            #Find 'smallest' date
                            print_slow("\nWhat date would you like to start the forecast from?")
                            smallest_date = collect_date("Date of transaction: ")
                            
                            #Find 'biggest' date
                            try: 
                                biggest_date = pot_forecasts[0][2]
                            except IndexError as e:  
                                print_slow(f"\nError: {e}")
                                print_slow("No forecasts recorded for this Vault")
                                break
                            
                            for forecast in pot_forecasts:
                                if forecast[2] > biggest_date:
                                    biggest_date = forecast[2]
                                else:
                                    continue
                            biggest_date = convert_date(biggest_date)

                            delta = biggest_date - smallest_date
                            delta_days = delta.days
                            delta_weeks = math.ceil(delta_days / 7)
                            
                            forecast_balance_pot(selected_pot, pots, smallest_date, delta_weeks)
                            break
                        else:
                            print_slow("\nOption not recognized, please try again.")
                            continue

                    break

                elif summary_action == "Forecast List":
                    
                    #reinstantiate forecasts
                    forecast_exists = False
                    res = cur.execute("SELECT * FROM forecasts")
                    returned_forecasts = res.fetchall()
                    if len(returned_forecasts) > 0:
                        forecast_exists = True
                    if forecast_exists == False:
                        pass
                    else:
                        forecasts, forecast_ids = re_forecasts(pots, vaults, pot_ids, user)
                    
                    #create forecast summary
                    forecast_summary(forecasts)
                    break

                elif summary_action == "Transaction List":
                    #reinstantiate transactions 
                    transaction_exists = False
                    res = cur.execute("SELECT * FROM transactions")
                    returned_transactions = res.fetchall()
                    if len(returned_transactions) > 0:
                        transaction_exists = True

                    if transaction_exists == False:
                        transactions = {}
                        transaction_ids = []

                    else:
                        transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                    #create transaction summary
                    transaction_summary(transactions)
                    break

                elif summary_action == "Exit":
                    print()
                    break

                else:
                    print_slow("Sorry, I don't recognize that instruction. Please try again.")

            continue

        elif action == "Delete":
            while True:
                print_slow('\n\033[1;31mDelete Menu\033[0m\n\nWhat would you like to delete? \n\n"Profile" to delete a user profile and all associated data, \n"Vault" to delete a specific vault, \n"Pot" to delete a specific pot, \n"Transaction" to delete a specific transaction, \n"Forecast" to delete a specific Forecast, \n"Exit" to return to main menu')
                delete_action = input()

                if delete_action == "Profile":
                    del_profile(user)
                    exit()

                elif delete_action == "Vault":
                    success = del_vault(user,vaults) #Delete vault
                    if success:
                        #reinstantiate vaults 
                        vaults, vault_ids = re_vaults(username, user)
                        #reinstantiate pots
                        pots, pot_ids = re_pots(vaults, vault_ids, user)
                        #reinstantiate transactions 
                        transaction_exists = False
                        res = cur.execute("SELECT * FROM transactions")
                        returned_transactions = res.fetchall()
                        if len(returned_transactions) > 0:
                            transaction_exists = True

                        if transaction_exists == False:
                            transactions = {}
                            transaction_ids = []
                        else:
                            transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                        print_slow("\nVault deleted succesfully")

                        break

                    else:
                        continue

                elif delete_action == "Pot":
                    success = del_pot(user,pots)
                    if success:
                        #reinstantiate vaults 
                        vaults, vault_ids = re_vaults(username, user)
                        #reinstantiate pots
                        pots, pot_ids = re_pots(vaults, vault_ids, user)
                        #reinstantiate transactions 
                        transaction_exists = False
                        res = cur.execute("SELECT * FROM transactions")
                        returned_transactions = res.fetchall()
                        if len(returned_transactions) > 0:
                            transaction_exists = True

                        if transaction_exists == False:
                            transactions = {}
                            transaction_ids = []

                        else:
                            transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                        break

                    else:
                        continue

                elif delete_action == "Transaction":
                    success = del_transaction(user,transactions)

                    if success:
                        #reinstantiate vaults 
                        vaults, vault_ids = re_vaults(username, user)
                        #reinstantiate pots
                        pots, pot_ids = re_pots(vaults, vault_ids, user)
                        #reinstantiate transactions 
                        transaction_exists = False
                        res = cur.execute("SELECT * FROM transactions")
                        returned_transactions = res.fetchall()
                        if len(returned_transactions) > 0:
                            transaction_exists = True

                        if transaction_exists == False:
                            transactions = {}
                            transaction_ids = []

                        else:
                            transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                        break

                    else:
                        continue

                elif delete_action == "Forecast":
                    forecast_id = int(input("\nEnter the forecast_id that you want to delete: \n\n").strip())
                    success = del_forecast(user,forecasts,forecast_id)

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
                            forecasts, forecast_ids = re_forecasts(pots, vaults, pot_ids, user)
                            print_slow("\nForecast deleted succesfully")
                        break

                    else:
                        print_slow(f"\nForecast '{forecast_id}' not found for user '{username}'.")
                        print_slow_nospace(f"Available forecasts for {username}: {[f.forecast_id for f in forecasts.values() if f.username == username]}")
                        continue

                elif delete_action == "Exit":
                    print()
                    break

                else:
                    print_slow_nospace("\nInput not recognized")

            continue

        elif action == "Instructions":
            print_slow_nospace("\n\033[1;31mInstructions\033[0m")
            print_slow(instructions())

        elif action == "Exit":
            con.close()
            print_slow("\nOK, the program will now terminate. See final values of the vaults and pots below. Thanks for using Money Pots!")
            summary(vaults, pots)
            exit()

        elif action == "":
            continue

        else:
            print_slow("\nInvalid command. Please try again")

if __name__ == "__main__":
    main()