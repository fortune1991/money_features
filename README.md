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

## Dependencies

The project requires:
- Python 3.6+
- [Tabulate](https://pypi.org/project/tabulate/) (for formatted output)

All dependencies are listed in [requirements.txt](requirements.txt)

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fortune1991/money_features.git
   cd money-pots

2. **Set-up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate # Linux/Mac
    venv\Scripts\activate # Windows

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

4. **Run the application**:
    ```bash
    python3 project.py

## Development Journey
### Key Achievements
- Implemented complex class relationships
- Developed complete SQLite integration
- Created robust CLI interface
- Designed forecast conversion system

### Future Roadmap
- Enhanced data analytics (grafana, more tabular information etc.)
- Project implimented as an API, deployed and hosted as AWS Lambda function
- PostgreSQL migration 
- Project implemented as a Web app, also deployed and hosted on AWS. 
