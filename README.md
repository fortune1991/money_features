# Money Pots  

## Description  
Money Pots is a comprehensive savings and budgeting tool that helps users organize their finances through a hierarchical system of Vaults and Pots.

## Key Features  

### Financial Organization  
- Create unlimited Vaults and Pots, to compartmentalize funds
- Track current balances across all accounts  
- View transaction histories  
- Manage future financial forecasts  

### Advanced Functionality  
- Automatic conversion of past-due forecasts into transactions 
- Weekly balance projections  
- Comprehensive summary reports  
- Data persistence through SQLite database  

## Technical Implementation  

### Object-Oriented Architecture  
Core classes:  
- **`User`**: Manages user profiles  
- **`Vault`**: Contains Pots and calculates aggregate values  
- **`Pot`**: Tracks individual budgets  
- **`Transaction`**: Records financial activities  
- **`Forecast`**: Manages future transactions  

### Database Schema  
SQLite tables:  
- `users`  
- `vaults`  
- `pots`  
- `transactions`  
- `forecasts`  

## Code Structure 
- project.py - Main application logic and menu system
- project_classes.py - All class definitions and methods
- project_functions.py - Helper functions and CRUD operations
- database.py - Database initialization and schema

## Installation



