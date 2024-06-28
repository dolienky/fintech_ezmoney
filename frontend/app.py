# Import libraries and necessary functions
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from web3 import Web3, Account
import json

# Initiate Flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' 

# Connect to Ganache
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    raise Exception("Could not connect to Ganache")

# Path to your Truffle build directory and JSON file
PATH_TRUFFLE_WK = '../backend/build/contracts/'
JSON_FILE = 'P2PLending.json'
json_file_path = PATH_TRUFFLE_WK + JSON_FILE

# Load the JSON file and extract ABI
with open(json_file_path, 'r') as f:
    truffle_data = json.load(f)
    abi = truffle_data['abi']

# Configurate the contract to connect frontend - backend
contract_address = '0x6663d3e004A311729750f0eF3E0701804eBaA3C4'
contract_abi= abi
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Load user data from Excel
def load_user_data():
    return pd.read_excel('../backend/user_data.xlsx')

# Save user data to Excel
def save_user_data(df):
    df.to_excel('../backend/user_data.xlsx', index=False)

# Route for welcoming page. Self-explanatory
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Take input as username and password
        username = request.form['username']
        password = request.form['password']
        
        # Compare it with the database. If both credentials are matching,
        #let users in
        users_df = load_user_data()        
        user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        
        # If successful, pass the information to the next screen
        if not user.empty:
            user_info = user.iloc[0]
            user_type = user_info['user_type']
            email = user_info['email']
            phone = user_info['phone']
            wallet_address = user_info['wallet_address']
            # Depends on user type, send them to the correct screen
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard', username=username, email=email, phone=phone, wallet_address=wallet_address))
            elif user_type == 'borrower':
                return redirect(url_for('borrower_dashboard', username=username, email=email, phone=phone, wallet_address=wallet_address))
            elif user_type == 'lender':
                return redirect(url_for('lender_dashboard', username=username, email=email, phone=phone, wallet_address=wallet_address))
        # If error, pop a warning
        else:
            error = "You have entered an invalid username or password"
            return render_template('login.html', error=error)    
    return render_template('login.html')

# Route for signing up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Take user input for registration
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        user_type = request.form['user_type']
        
        # Load the database
        users_df = load_user_data()
        
        # Compare the username, if exists, pop taken
        if username in users_df['username'].values:
            error_username = "Username already taken"
            return render_template('signup.html', error_username=error_username)
        
        # Generate wallet address and private key
        account = Account.create()
        wallet_address = account.address
        private_key = account.key.hex()
        
        # Write into existing dataframe
        new_user = pd.DataFrame({
            'username': [username],
            'password': [password],
            'email': [email],
            'phone': [phone],
            'user_type': [user_type],
            'wallet_address': [wallet_address]
        })
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        save_user_data(users_df)
        
        # Redirect to disclaimer page with private key
        return render_template('disclaimer.html', private_key=private_key)    
    return render_template('signup.html')

# Route for disclaimer page
@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

# Route for admin dashboard, nothing for now
@app.route('/admin_dashboard')
def admin_dashboard():
    username = request.args.get('username')
    email = request.args.get('email')
    phone = request.args.get('phone')
    wallet_address = request.args.get('wallet_address')
    return render_template('admin_dashboard.html', username=username, email=email, phone=phone, wallet_address=wallet_address)

# Route for borrower dashboard
@app.route('/borrower_dashboard')
def borrower_dashboard():
    # Take username and wallet_address from login screen
    username = request.args.get('username')
    wallet_address = request.args.get('wallet_address')
    
    # Retrieve the wallet balance
    balance = web3.eth.get_balance(wallet_address)
    wallet_balance = web3.from_wei(balance, 'wei')
    wallet_balance = int(wallet_balance)
    wallet_balance = wallet_balance / (0.00031) / (10**18)
    wallet_balance = int(wallet_balance)    
    return render_template('borrower_dashboard.html', 
                           username=username, 
                           wallet_address=wallet_address,
                           wallet_balance=wallet_balance) 

# This is an imaginary route to trigger the smart contract
@app.route('/create_loan_request', methods=['POST'])
def create_loan_request():
    # Take username and wallet_address from the previous screen
    # The loan amount is converted to Wei, the mimimum currency of Ethereum
    #to avoid float data
    username = request.form['username']
    wallet_address = request.form['wallet_address']
    loan_amount = int(int(request.form['loan_amount']) * 0.00031 * (10**18))
    loan_duration = int(request.form['loan_duration'])
    interest_rate = int(request.form['interest_rate'])
    loan_purpose = request.form['loan_purpose']

    # Calling a function on the smart contract
    tx_hash = contract.functions.createLoanRequest(username, wallet_address, loan_amount, loan_duration, interest_rate, loan_purpose).transact({'from': web3.eth.accounts[0]})
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return redirect(url_for('borrower_dashboard', 
                            username=username, 
                            wallet_address=wallet_address))

# Router for borrower's loan management                           
@app.route('/borrower_loan_management')
def borrower_loan_management():
    #Call 2 functions from the smart contract to retrieve all loan info
    loans = []
    num_requests = contract.functions.getNumLoanRequests().call()

    for i in range(num_requests):
        loan = contract.functions.getLoanRequest(i).call()
        loans.append({
            'id': loan[0],
            'amount': int(loan[3] * (1/0.00031) / (10**18)),
            'interestRate': loan[4],
            'duration': loan[5],
            'monthlyPayment': int(loan[9] * (1/0.00031) / (10**18)),
            'remainingPayment': int(loan[10] * (1/0.00031) / (10**18)),
            'funded': loan[7],
            'lender': loan[11],
        })
    return render_template('borrower_loan_management.html', loans=loans)

# Route for borrower's confirmation
@app.route('/borrower_confirmation', methods=['POST', 'GET'])
def borrower_confirmation():
    if request.method == 'POST':
        # Take loan id, monthly payment, and lender wallet address from
        #the previous screen
        loan_id = request.form['loan_id']
        monthly_payment = request.form['monthly_payment']
        lender_wallet_address = request.form['lender_wallet_address']
        loan = {
            'id': loan_id,
            'monthlyPayment': monthly_payment,
            'lender': lender_wallet_address
        }
        return render_template('borrower_confirmation.html', loan=loan)
    else:
        return redirect(url_for('borrower_loan_management'))

# This is an imaginary route to trigger a function in the smart contract
@app.route('/repay_loan', methods=['POST'])
def repay_loan():
    # Take loan id, monthly payment, and lender wallet address from
    #the previous screen
    loan_id = int(request.form['loan_id'])
    monthly_payment = float(request.form['monthly_payment'])
    private_key = request.form['private_key']
    # Convert amount in EUR to Wei
    amount_in_wei = int(monthly_payment * (10**18) * 0.00031)
    # Unlock the account associated with the private key
    account = web3.eth.account.from_key(private_key)
    web3.eth.default_account = account.address
    # Call the repayLoan function in the contract
    tx_hash = contract.functions.repayLoan(loan_id).transact({'value': amount_in_wei})
    # Wait for transaction receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return "Repay successfully"

# Route for lender dashboard
@app.route('/lender_dashboard')
def lender_dashboard():
    # Retrieve all loan requests from the smart contract
    loans = []
    wallet_address = request.args.get('wallet_address')
    
    # Retrieve the wallet balance
    balance = web3.eth.get_balance(wallet_address)
    wallet_balance = web3.from_wei(balance, 'wei')
    wallet_balance = int(wallet_balance)
    wallet_balance = wallet_balance / (0.00031) / (10**18)
    wallet_balance = int(wallet_balance)
    
    # Retrieve loan's info by calling 2 functions from the smart contract
    num_requests = contract.functions.getNumLoanRequests().call()
    for i in range(num_requests):
        loan = contract.functions.getLoanRequest(i).call()
        loans.append({
            'id': loan[0],
            'username': loan[1],
            'wallet_address': loan[2],
            'amount': int(loan[3] * (1/0.00031) / (10**18)),
            'interestRate': loan[4],
            'duration': loan[5],
            'purpose': loan[6],
            'funded': loan[7]
        })
    return render_template('lender_dashboard.html', loans=loans,
                           wallet_balance = wallet_balance,
                           wallet_address = wallet_address)

# Route for lender's loan management
@app.route('/lender_loan_management')
def lender_loan_management():
    # Get wallet address from the previous screen
    wallet_address = request.args.get('wallet_address')
    loans = []
    # Retrieve loan's info by calling 2 functions from the smart contract
    num_requests = contract.functions.getNumLoanRequests().call()
    for i in range(num_requests):
        loan = contract.functions.getLoanRequest(i).call()
        if loan[11] == wallet_address:        
            loans.append({
                'id': loan[0],
                'amount': int(loan[3] * (1/0.00031) / (10**18)),
                'interestRate': loan[4],
                'duration': loan[5],
                'monthlyPayment': int(loan[9] * (1/0.00031) / (10**18)),
                'remainingPayment': int(loan[10] * (1/0.00031) / (10**18)),
                'funded': loan[7],
                'lender': loan[11],
            })               
        else:
            continue
    return render_template('lender_loan_management.html', loans=loans,
                           wallet_address = wallet_address)

# Route for lender's confirmation
@app.route('/lender_confirmation', methods=['POST', 'GET'])
def lender_confirmation():
    # Retrieve loan's info by calling 2 functions from the smart contract
    loans = []
    num_requests = contract.functions.getNumLoanRequests().call()
    for i in range(num_requests):
        loan = contract.functions.getLoanRequest(i).call()
        loans.append({
            'id': loan[0],
            'username': loan[1],
            'wallet_address': loan[2],
            'amount': loan[3] * (1/0.00031) / (10**18),
            'interestRate': loan[4],
            'duration': loan[5],
            'purpose': loan[6],
            'funded': loan[7]})
    
    if request.method == 'POST':
        loan_id = int(request.form['loan_id'])
        
        # Retrieve loan details from blockchain (replace with actual logic)
        loan = next((loan for loan in loans if loan['id'] == int(loan_id)), None)
        if loan:
            # Pass loan details and lender information to lender_confirmation.html
            return render_template('lender_confirmation.html', loan=loan)
        else:
            # Handle case where loan ID not found
            return "Loan ID not found"
    
    # Handle GET request (initial landing on confirmation page)
    return redirect(url_for('lender_dashboard'))

# Imaginary route to activate a function from the smart contract
@app.route('/fund_loan', methods=['POST'])
def fund_loan():
    if request.method == 'POST':
        # Retrieve loan details
        loans = []
        num_requests = contract.functions.getNumLoanRequests().call()
        for i in range(num_requests):
            loan = contract.functions.getLoanRequest(i).call()
            loans.append({
                'id': loan[0],
                'username': loan[1],
                'wallet_address': loan[2],
                'amount': loan[3],
                'interestRate': loan[4],
                'duration': loan[5],
                'purpose': loan[6],
                'funded': loan[7]
            })
        # Take loan_id and private_key from user's input
        loan_id = int(request.form['loan_id'])
        private_key = request.form['private_key']
    
        loan = next((loan for loan in loans if loan['id'] == int(loan_id)), None)
        amount_in_wei = int(loan['amount'])
        # Unlock the account associated with the private key
        account = web3.eth.account.from_key(private_key)
        web3.eth.default_account = account.address
        # Call the fundLoan function in the contract
        tx_hash = contract.functions.fundLoan(loan_id).transact({'value': amount_in_wei})
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return "Loan funded successfully!"

if __name__ == '__main__':
    app.run(debug=True)
