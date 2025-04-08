import datetime, os, sqlite3
from project_classes import User, Vault, Pot, Transaction
from project_functions import submit_transaction, print_slow, print_slow_nospace, int_validator, collect_date, convert_date, summary, create_pot, create_user, create_vault, create_profile, instructions, re_vaults, re_pots, re_transactions, count_pots, count_transactions, count_vaults, transaction_summary
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
    
    # check if database exists

    database_exists = os.path.isfile("/Users/michaelfortune/Developer/projects/money/money_features/money.db")
    
    if not database_exists:

        create_database()
        print_slow("""
Welcome to Money Pots, your savings and budgeting calculator.""")
        print_slow(instructions())
        
        user, vaults, pots = create_profile()
    
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

            # SQL QUERY TO DETERMINE IF USER EXISTS

            res = cur.execute("SELECT username FROM users")
            returned_users = res.fetchall()
            for user in returned_users:
                if login == user[0]:
                    user_exists = True
            
           # REINSTANTIATE OBJECTS FROM DATABASE
                        
            if user_exists == True:
                print()
                print_slow("Welcome back to Money Pots")
                #reinstantiate user
                user = create_user(login)
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

                # Update Pots and Vaults values - UPDATE THIS LOGIC, SO IT ONLY UPDATES VALUES BASED ON TODAYS DATE (NOT FUTURE ONES)

                for pot in pots.values():
                    pot.pot_value()
                
                for vault in vaults.values():
                    vault.vault_value()

                con.close()
                break

            else:
                con.close()
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
                    print_slow("\nUnknown Command. Please try to login again")                
     
# Loop on Command line until exit

    # Establish DB Connection
    
    db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db" 
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    while True:
        print_slow('Now, I await your commands to proceed. Please type: \n\n"New" to submit a new item (profile, vaults, pots, transactions, forecasts), \n"Summary" to get either a balance report, forecast report or transactions summary, \n"Delete" to remove an item, \n"Instructions" to get further information on how to use Money Pots, \n"Exit" to terminate the programme')
        action = input()
        if action == "New":
            while True:
                print_slow('\nWhat type of new item would you like to create? \n\n"Profile" to create a new user profile, \n"Vault" to create a new vault, \n"Pot" to create a new pot, \n"Transaction" to submit a new transaction, \n"Forecast" to submit an estimate for predicted spending')
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
                    vault_data = [(vaults[f"vault_{(vault_count + 1)}"].vault_id,
                    vaults[f"vault_{(vault_count + 1)}"].vault_name,
                    vaults[f"vault_{(vault_count + 1)}"].start,
                    vaults[f"vault_{(vault_count + 1)}"].end,
                    vaults[f"vault_{(vault_count + 1)}"].username)]

                    # Insert vaults data into the database
                    cur.executemany("INSERT INTO vaults VALUES(?, ?, ?, ?, ?)", vault_data)
                    con.commit()
                    
                    # Create associated pots
                    print_slow_nospace("Now, let's create at least one pot to associate with this vault")
                    pot_count = count_pots()
                    selected_vault = vaults.get(f"vault_{(vault_count + 1)}")

                    pots[f"pot_{(pot_count + 1)}"] = create_pot(pot_count, selected_vault, user)

                    pot_data = [(pots[f"pot_{(pot_count + 1)}"].pot_id, 
                    pots[f"pot_{(pot_count + 1)}"].pot_name, 
                    pots[f"pot_{(pot_count + 1)}"].start, 
                    pots[f"pot_{(pot_count + 1)}"].end, 
                    pots[f"pot_{(pot_count + 1)}"].vault_id, 
                    pots[f"pot_{(pot_count + 1)}"].amount, 
                    pots[f"pot_{(pot_count + 1)}"].username)]

                    # Insert pots data into the database
                    cur.executemany("INSERT INTO pots VALUES(?, ?, ?, ?, ?, ?, ?)", pot_data)
                    con.commit()

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

                                pot_data = [(pots[f"pot_{(pot_count + 1)}"].pot_id, 
                                pots[f"pot_{(pot_count + 1)}"].pot_name, 
                                pots[f"pot_{(pot_count + 1)}"].start, 
                                pots[f"pot_{(pot_count + 1)}"].end, 
                                pots[f"pot_{(pot_count + 1)}"].vault_id, 
                                pots[f"pot_{(pot_count + 1)}"].amount, 
                                pots[f"pot_{(pot_count + 1)}"].username)]

                                # Insert pots data into the database
                                cur.executemany("INSERT INTO pots VALUES(?, ?, ?, ?, ?, ?, ?)", pot_data)
                                con.commit()
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
                    no_transactions = 1
                    while True:
                        try:
                            for x in range(no_transactions):
                                while True: 
                                    # Count existing transactions
                                    start_transaction = count_transactions()
                                    
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
                                        transactions[f"transaction_{x+1}"] = submit_transaction(start_transaction, selected_pot, selected_vault, user)
                                        selected_pot.pot_value()
                                        break
                                    else:
                                        print_slow(f"pot '{pot_input}' not found. Please enter a valid pot name.")
                                        
                            action = ""
                            break
                        
                        except ValueError as e:  
                            print_slow(f"Error: {e}")
                            
                        except Exception as e:  
                            print_slow(f"An unexpected error occurred: {e}")
                            
                    break
                    
                elif new_action == "Forecast":
                    while True:
                        print_slow('\nOK, would you like to submit a "Single expense" or a "Weekly expense"? or "Exit" to return')
                        expense = input()

                        if expense == "Single expense":
                            single = int(input("\nWhat's the amount of your predicted expenditure? \n\n"))
                            print_slow("\nExcellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
                            
                            while True:
                                expense_date = collect_date("Date of transaction: ")
                                today = datetime.datetime.today()
                                if expense_date < today:
                                    print_slow("\nInvalid Date")
                                else:
                                    print_slow(f"\n{str(today)}")
                                    print_slow("Single expense recorded")
                                    break
                            
                        elif expense == "Weekly expense":    
                            weekly = int(input("\nWhat's your predicted weekly expenditure? "))
                            no_weeks = int(input("\nHow many weeks is this for? "))
                            print_slow("\nExcellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
                            
                            while True:
                                expense_start_date = collect_date("Date of transaction: ")
                                today = datetime.datetime.today()
                                if expense_start_date < today:
                                    print_slow("\nInvalid Date")
                                else:
                                    print_slow(f"\n{str(today)}")
                                    print_slow("Weekly expense recorded")
                                    break
                            
                        elif expense == "Exit":
                            print()
                            break
                            
                        else:
                            print_slow("\nPlease enter a valid expense type ('Single expense', 'Weekly expense', or 'Exit' to return")
                        
                        break

                action = ""
                break

        if action == "Summary":
            while True:
                print_slow('\nWhat type of summary would you like to create? \n\n"Balance Summary" to show your vaults and pots balances, \n"Forecast Summary" to show your predicted future balances based on your forecast expenditure, \n"Transaction Summary" to show a list of all your recorded transactions')
                summary_action = input()

                if summary_action == "Balance Summary":
                    summary(vaults, pots)
                    break

                elif summary_action == "Forecast Summary":
                    print_slow("\nForecast Summary")
                    break

                elif summary_action == "Transaction Summary":
                    transaction_summary(transactions)
                    break

                else:
                    print_slow("Sorry, I don't recognize that instruction. Please try again.")

            continue

        elif action == "Delete":
            while True:
                print_slow('\nWhat would you like to delete? \n\n"Profile" to delete a user profile and all associated data, \n"Vault" to delete a specific vault, \n"Pot" to delete a specific pot, \n"Transaction" to delete a specific transaction, \n"Forecast" to delete a specific Forecast')
                summary_action = input()

                if summary_action == "Profile":
                    try:
                        # Get the username before deleting
                        username = user.username

                        # Delete all related data first
                        cur.execute("DELETE FROM transactions WHERE username = ?", (username,))
                        cur.execute("DELETE FROM pots WHERE username = ?", (username,))
                        cur.execute("DELETE FROM vaults WHERE username = ?", (username,))

                        # Finally, delete the user
                        cur.execute("DELETE FROM users WHERE username = ?", (username,))
                        
                        con.commit()
                        print_slow("\nProfile deleted successfully.")

                    except sqlite3.Error as e:
                        print_slow(f"\nError deleting profile: {e}")

                    exit()

                elif summary_action == "Vault":
                    
                    vault_name = input("\nEnter the name of the Vault you want to delete: \n\n").strip()
                    username = user.username  # Get the current user's username

                    # Search for the vault that matches both the name and the username
                    selected_vault = None
                    for vault in vaults.values():
                        if vault.vault_name == vault_name and vault.username == username:
                            selected_vault = vault
                            break

                    if selected_vault:
                        vault_id = selected_vault.vault_id
                        # Proceed with deletion of related data first
                        cur.execute("DELETE FROM transactions WHERE vault_id = ?", (vault_id,))
                        cur.execute("DELETE FROM pots WHERE vault_id = ?", (vault_id,))

                        # Finally delete the vault
                        cur.execute("DELETE FROM vaults WHERE vault_id = ?", (vault_id,))
                        con.commit()

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
                            pass

                        else:
                            transactions, transaction_ids = re_transactions(pots, vaults, pot_ids, user)

                        print_slow("\nVault deleted succesfully")
                        break

                    else:
                        print_slow(f"Vault '{vault_name}' not found for user '{username}'.")
                        print_slow(f"Available vaults for {username}: {[v.vault_name for v in vaults.values() if v.username == username]}")

                elif summary_action == "Pot":
                    print_slow("Delete Pot")
                    break

                elif summary_action == "Transaction":
                    print_slow("Delete Transaction")
                    break

                elif summary_action == "Forecast":
                    print_slow("Delete Forecast")
                    break

                else:
                    print_slow("Input not recognized")

            continue

        elif action == "Instructions":
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

# Add feature within infinite loop for "Forecasting". This should allow users to submit prospective transactions 
# in two different formats. "single expense" and "weekly expense". After each expense is submitted, the programme
# should output a pretty print table to show the model results of budget vs expenditure. If previsouly submitted transactions
# are now present (or past), then the programme should ask the user to update and then approve the forecasts. These will be updated
# in the SQL database as transactions.

# Create/Improve print and reporting functions using Tabulate
# Add Exit function to "New" and "Delete"
# Continue to Write Delete Function. Start from "Pots"
# Write Forecasting Function
# Make sure pot dates sit within the boundaries of the vault date
# Make sure transaction and forecast dates sit within the boundaries of the pot date
# Tidy up comments to make code more readable
# Write code tests
# Use programme for a while
# Type up blog posts

if __name__ == "__main__":
    main()