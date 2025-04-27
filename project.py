import datetime,os,sqlite3,math
from project_classes import User,Vault,Pot,Transaction
from project_functions import submit_forecast,transfer_transaction,submit_transaction,print_slow,print_slow_nospace,int_validator,collect_date,convert_date,summary,create_pot,create_user,create_vault,create_profile,instructions,re_user,re_vaults,re_pots,re_transactions,re_forecasts,count_pots,count_transactions,count_vaults,count_forecasts,transaction_summary,forecast_summary,del_profile,del_vault,del_pot,del_transaction,del_forecast,forecast_balance_vault,forecast_balance_pot,user_exist,refresh_user_data
from tabulate import tabulate
from time import sleep
from database import create_database

import warnings
warnings.filterwarnings("ignore",message="The default datetime adapter is deprecated",category=DeprecationWarning)

def main():
    vaults = {}
    pots = {}
    transactions = {}
    forecasts = {}

    db_path = "/Users/michaelfortune/Developer/projects/money/money_features/money.db"
    database_exists = os.path.isfile(db_path)
    if not database_exists:

        create_database()
        print_slow("""
Welcome to Money Pots, your savings and budgeting calculator.""")
        print_slow(instructions())
        user,vaults,pots = create_profile(con)
        username = user.username[0]
    
    if database_exists:
        #log user in
        while True:
            # Establish a connection to the Database
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            print_slow("""
Welcome to Money Pots, your savings and budgeting calculator. Let me help you to login and view your profile. What's your username?""")
            login = input().strip() # Remove trailing white space
            user_exists = user_exist(con,login)
           # if user exists, reinstantiate objects from the database
            if user_exists == True:
                print()
                print_slow_nospace("Welcome back to Money Pots")
                user = re_user(con,login)
                username = user.username[0]
                #refresh user data
                vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
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
                    user,vaults,pots = create_profile(con)
                    break
                elif response == "Try again":
                    continue
                elif response == "Exit":
                    exit()
                else:
                    print_slow_nospace("\nUnknown Command. Please try to login again")    
                 
# Loop Menu on Command line until exit

    while True:
        print_slow('\n\033[1;31mMain Menu\033[0m\n\nNow, I await your commands to proceed. Please type: \n\n"New" to submit a new item (profile, vaults, pots, transactions, forecasts), \n"Summary" to get either a balance report, forecast report or transactions summary, \n"Delete" to remove an item, \n"Instructions" to get further information on how to use Money Pots, \n"Exit" to terminate the programme')
        action = input()
        if action == "New":
            while True:
                print_slow('\nWhat type of new item would you like to create? \n\n\033[1;31mNew Items Menu\033[0m \n\n"Profile" to create a new user profile, \n"Vault" to create a new vault, \n"Pot" to create a new pot, \n"Transaction" to submit a new transaction, \n"Forecast" to submit an estimate for predicted spending, \n"Exit" to return back to main menu')
                new_action = input()

                if new_action == "Profile":
                    print_slow("\nExcellent. Please answer the following questions to create a new user profile")
                    transactions= {}
                    forecasts = {}
                    user,vaults,pots = create_profile(con)
                    break

                elif new_action == "Vault":
                    vault_count = count_vaults(con)
                    vaults[f"vault_{(vault_count + 1)}"] = create_vault(con,vault_count,user,username)
                    
                    # Create associated pots
                    print_slow_nospace("Now, let's create at least one pot to associate with this vault")
                    pot_count = count_pots(con)
                    selected_vault = vaults.get(f"vault_{(vault_count + 1)}")

                    pots[f"pot_{(pot_count + 1)}"] = create_pot(con,pot_count,selected_vault,user,username)
                    action = ""
                    break

                elif new_action == "Pot":
                    while True:
                        try:
                            print_slow("\nWhat vault will this pot be assigned to? ")
                            pot_vault = input()
                            pot_count = count_pots(con)
                            selected_vault = None
                            for vault in vaults.values():
                                if vault.vault_name == pot_vault and vault.username == user.username:
                                    selected_vault = vault

                            if selected_vault:
                                pots[f"pot_{(pot_count + 1)}"] = create_pot(con,pot_count,selected_vault,user)

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
                                start_transaction = count_transactions(con)
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
                                    transactions[f"transaction_{1}"] = submit_transaction(con,start_transaction,selected_pot,selected_vault,user,username)
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
                                types = ["in","out"]
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
                                    start_forecast = count_forecasts(con)
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
                                        forecasts[f"forecast_{1}"] = submit_forecast(con,forecast_name,start_forecast,selected_pot,selected_vault,user,username,expense_date,single,forecast_type)
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
                                types = ["in","out"]
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
                            print_slow("\nExcellent. Now we'll define when the transaction will take place. Please note, all date input values must be in the format DD/MM/YY")
                            
                            while True:
                                expense_date = collect_date("Date: ")
                                today = datetime.datetime.today()
                                date_list = {}
                                if expense_date < today:
                                    print_slow("\nInvalid Date, must be in the future for a forecast")
                                else:
                                    for i in range (0,no_weeks,1):
                                        date = expense_date + datetime.timedelta(days=(7*i))
                                        date_list[i] = date
                                    break

                            try:
                                while True: 
                                    start_forecast = count_forecasts(con)
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
                                        for key,date in date_list.items():
                                            forecasts[f"forecast_{key}"] = submit_forecast(con,forecast_name,(start_forecast + key),selected_pot,selected_vault,user,username,date,weekly,forecast_type)
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
                    #refresh user data
                    vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                    #create balance summary
                    summary(vaults,pots)
                    break

                if summary_action == "Forecast Balance Report":
                    #refresh user data
                    vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                    while True:
                        print_slow('\nWould you like to forecast the balance for a "Vault" or "Pot"?')
                        option = input()

                        if option == "Vault":
                            forecast_balance_vault(con,vaults,pots,username)
                            break

                        elif option == "Pot":
                            forecast_balance_pot(con,pots,username)
                            break
                        else:
                            print_slow_nospace("\nOption not recognized, please try again.")
                            continue

                    break

                elif summary_action == "Forecast List":
                    #refresh user data
                    vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                    #create forecast summary
                    forecast_summary(forecasts)
                    break

                elif summary_action == "Transaction List":
                    #refresh user data
                    vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                    #create transaction summary
                    transaction_summary(transactions)
                    break

                elif summary_action == "Exit":
                    print()
                    break

                else:
                    print_slow_nospace("Sorry, I don't recognize that instruction. Please try again.")

            continue

        elif action == "Delete":
            while True:
                print_slow('\n\033[1;31mDelete Menu\033[0m\n\nWhat would you like to delete? \n\n"Profile" to delete a user profile and all associated data, \n"Vault" to delete a specific vault, \n"Pot" to delete a specific pot, \n"Transaction" to delete a specific transaction, \n"Forecast" to delete a specific Forecast, \n"Exit" to return to main menu')
                delete_action = input()

                if delete_action == "Profile":
                    del_profile(con,user,username)
                    exit()

                elif delete_action == "Vault":
                    success = del_vault(con,user,vaults,username) #Delete vault
                    if success:
                        #refresh user data
                        vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                        break
                    else:
                        continue

                elif delete_action == "Pot":
                    success = del_pot(con,user,pots,username)
                    if success:
                        #refresh user data
                        vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                        break
                    else:
                        continue

                elif delete_action == "Transaction":
                    success = del_transaction(con,user,transactions,username)
                    if success:
                        #refresh user data
                        vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                        break
                    else:
                        continue

                elif delete_action == "Forecast":
                    forecast_id = int(input("\nEnter the forecast_id that you want to delete: \n\n").strip())
                    success = del_forecast(con,user,forecasts,forecast_id,username)
                    if success:
                        #refresh user data
                        vaults, vault_ids,pots,pot_ids,transactions,transaction_ids,forecasts,forecast_ids = refresh_user_data(con,user,username)
                        break
                    else:
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
            cur.close()
            con.close()
            print_slow("\nOK, the program will now terminate. See final values of the vaults and pots below. Thanks for using Money Pots!")
            summary(vaults,pots)
            exit()

        elif action == "":
            continue

        else:
            print_slow("\nInvalid command. Please try again")

if __name__ == "__main__":
    main()