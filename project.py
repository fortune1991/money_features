import datetime, os, sqlite3
from project_classes import User, Vault, Pot, Transaction
from project_functions import submit_transaction, print_slow, int_validator, collect_date, convert_date, summary, create_pot, create_user, create_vault, create_profile, instructions, re_vaults, re_pots, re_transactions, count_pots, count_transactions, count_vaults, transaction_summary
from time import sleep
from database import create_database

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
Welcome to Money Pots, your savings and budgeting calculator.
        """)
        print_slow(instructions())
        
        user, vaults, pots = create_profile()
    
    if database_exists:

        # Establish a connection to the Database
        db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db" 
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        #log user in
        while True:
            print_slow("""
Welcome to Money Pots, your savings and budgeting calculator. Let me help you to login and view your profile. What's your username?
    """)
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
                    transactions, transaction_ids = re_transactions(pots, pot_ids, user)

                # Update Pots and Vaults values - UPDATE THIS LOGIC, SO IT ONLY UPDATES VALUES BASED ON TODAYS DATE (NOT FUTURE ONES)

                for pot in pots.values():
                    pot.pot_value()
                
                for vault in vaults.values():
                    vault.vault_value()

                con.close()
                break

            else:
                con.close()
                print()
                print("User doesn't exist. Respond 'Try again' 'New user' or 'Exit'")    
                print()

                response = input()

                if response == "New user":
                    print()
                    print("Excellent. Please answer the following questions to create a new user profile")
                    user, vaults, pots = create_profile()
                    break
                elif response == "Try again":
                    continue
                elif response == "Exit":
                    exit()
                else:
                    print("Unknown Command. Please try to login again")                
     
    # Loop on Command line until exit

    # Establish DB Connection
    db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db" 
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    while True:
        print_slow('Now, I await your commands to proceed. Please type: \n\n "Transaction" to submit a new transaction, \n "Transaction Activity" to list all user transactions, \n "Summary" to get a report of vault/pot values, \n "Instructions" to get a further information on how to use Money Pots \n "Vault" to create a new vault \n "Pot" to create a new pot \n "Forecasting" to model predicted expenditure, \n "Delete" to remove something, \n "Exit" to terminate the programme')
        print()
        print()
        action = input()

        if action == "Transaction":
    
        # Submit Transactions 

            print_slow("Excellent. Now, let me help you create a new transaction.")
            print()
            no_transactions = 1
            
            while True:
                try:
                    for x in range(no_transactions):
                        print(f"Transaction {x+1}")
                        print()
                        
                        while True: 
                              
                            # Count existing transactions
                            
                            start_transaction = count_transactions()
                            
                            print_slow("What pot should this pot be assigned to?: ")
                            pot_input = input()

                            # Find the pot using a simple loop
                            selected_pot = None
                            for pot in pots.values():
                                if pot.pot_name == pot_input and pot.username == user.username: 
                                    selected_pot = pot
                                    break

                            if selected_pot:
                                transactions[f"transaction_{x+1}"] = submit_transaction(start_transaction, selected_pot, user)
                                selected_pot.pot_value()
                                break
                            else:
                                print(f"pot '{pot_input}' not found. Please enter a valid pot name.")
                                print()
                    break
                
                except ValueError as e:  
                    print(f"Error: {e}")
                    print()

                except Exception as e:  
                    print(f"An unexpected error occurred: {e}")
                    print()
            
            print()

        # Print Summary

        elif action == "Summary":

            summary(vaults, pots)
            print()

        # Print Instructions

        elif action == "Instructions":
            print_slow(instructions())

        # Create new Vault

        elif action == "Vault":
            vault_count = count_vaults()
            vaults[f"vault_{(vault_count + 1)}"] = create_vault(vault_count, user)

            vault_data = [(vaults[f"vault_{(vault_count + 1)}"].vault_id,
            vaults[f"vault_{(vault_count + 1)}"].vault_name,
            vaults[f"vault_{(vault_count + 1)}"].start,
            vaults[f"vault_{(vault_count + 1)}"].end,
            vaults[f"vault_{(vault_count + 1)}"].username)]

            print()

            # Insert vaults data into the database
            cur.executemany("INSERT INTO vaults VALUES(?, ?, ?, ?, ?)", vault_data)
            con.commit()
        
        # Create new Pot

        elif action == "Pot":
            while True:
                try:
                    print_slow("What vault will this pot be assigned to? ")
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

                    else:
                        print(f"Vault '{vault_input}' not found. Please enter a valid vault name.")
                        print()
                
    
                except ValueError as e:  
                    print(f"Error: {e}")
                    print("Please try again")
                    print()

                except Exception as e:  
                    print(f"An unexpected error occurred: {e}")
                    print("Please try again")
                    print()
        
        # Forecasting - START HERE!

        elif action == "Forecasting":

            while True:
                print_slow('OK, would you like to submit a "single expense" or a "weekly expense"? \n\n')
                expense = input()

                if expense == "single expense":
                    single = int(input("What's the amount of your predicted expenditure? "))
                    print_slow("Excellent. Now we'll define when the transaction took place. Please note, all date input values must be in the format DD/MM/YY")
                    print()
                    print()
                    while True:
                        expense_date = collect_date("Date of transction: ")
                        today = datetime.datetime.today()
                        if expense_date < today:
                            print_slow("Invalid Date\n")
                        else:
                            print(today)
                            break
                    break
        
                elif expense == "weekly expense":
                    weekly = int(input("What's your predicted weekly expenditure? "))
                    expense_start_date = collect_date("Date of transction: ")
                    today = date.today()
                    print(today)
                    break
                else:
                    print_slow("Please enter a valid expense type")
                    break
        
        
        # Print list of user Transactions - MAKE THIS MORE LIKE THE PRINT SUMMARY FUNCTION!

        elif action == "Transaction Activity":
            transaction_summary(transactions)
            print()

            #res = cur.execute("SELECT * FROM transactions WHERE username = ?", (user.username,))
            #returned_transactions = res.fetchall()
            #print(returned_transactions)
            #print()
        
        
        elif action == "Delete":
            pass

            # Forecast
            
            # Transaction

            # Pot

            # Vault

            # User

        # Exit

        elif action == "Exit":
            con.close()
            print_slow("OK, the program will now terminate. See final values of the vaults and pots below. Thanks for using Money Pots!")
            print()
            summary(vaults, pots)
            print()
            exit()

        else:
            print_slow("Invalid command. Please try again")
            print()

        

# Add feature within infinite loop for "Forecasting". This should allow users to submit prospective transactions 
# in two different formats. "single expense" and "weekly expense". After each expense is submitted, the programme
# should output a pretty print table to show the model results of budget vs expenditure. If previsouly submitted transactions
# are now present (or past), then the programme should ask the user to update and then approve the forecasts. These will be updated
# in the SQL database as transactions.

# Do a GIT commit 
# Update instructions and messages
# Tidy up Loop
# Write Delete Function
# Write Forecasting Function
# Create/Improve print and reporting functions. NEED SQL Table Function?
# Make sure pot dates sit within the boundaries of the vault date
# Make sure transaction and forecast dates sit within the boundaries of the pot date
# Tidy up comments to make code more readable
# Write code tests
# Use programme for a while
# Type up blog posts


# "New" to submit a new item (profile, vaults, pots, transactions, forecasts)
# "Summary" to get either a balance report, forecast report, transactions summary
# "Delete" to remove an item
# "Exit" to terminate the programme


if __name__ == "__main__":
    main()