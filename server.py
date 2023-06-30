import subprocess
import traceback
import json
import requests
import logging
from datetime import datetime

from werkzeug.utils import secure_filename
import os
import threading


from flask import Flask, request, jsonify, redirect, render_template, flash, send_from_directory, url_for, session, redirect, Response, send_file

app = Flask(__name__)
app.secret_key = 'L1bqu5SocxW4CkoUR6bmCf3TE2twJByPhE2DJF3PFmrJTBPfhdBp'

def change_directory():
    os.chdir('/mnt/c/Users/OMAR/Desktop/novoWeb/novo-0.3.1/src')

    os.environ['FLASK_APP'] = 'server.py'  # Remplacez par le nom de votre fichier Python principal

    # Exécuter la commande flask run dans un processus séparé
    subprocess.Popen(['flask', 'run'])


def run_command():
    command = ['./novod', '-server']
    subprocess.Popen(command)


@app.before_request
def before_request():
    change_directory()
    run_command()
    
def create_wallet_thread(wallet_name, rpc_password, rpc_user):
    command = f"./novod -wallet={wallet_name} -rpcuser={rpc_user} -rpcpassword={rpc_password}"
    try:
        subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating wallet: {str(e)}")

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/create_wallet', methods=['GET', 'POST'])
def create_wallet():
    if request.method == 'POST':
        wallet_name = request.form.get('wallet_name')
       

        thread = threading.Thread(target=create_wallet_thread, args=(wallet_name))
        thread.start()

        return redirect('/login')
    else:
        return render_template('create_wallet.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        # Perform authentication logic here
        if username == "user" and password == "pass":
            cmd = f"./novod -rpcuser={username} -rpcpassword={password}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            return render_template('mainer.html', output=output)  # Render mainer.html template
        else:
            return "Login failed!"

    # GET request, show login page
    return render_template('login.html')

@app.route('/mainer.html')
def mainer():
    output = request.args.get('output')  # Retrieve output from the query parameters

    # Replace this with your actual code to get the result
    result = get_result()

    if result is None:
        # Handle the case when result is not available
        # You can redirect to an error page or return an error message
        return "Error: Result not available"
    return render_template('mainer.html', output=output)

@app.route('/get_balance')
def get_balance():
    account = request.args.get('account')
    command = ['./novo-cli', 'getbalance', account] if account else ['./novo-cli', 'getbalance']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode().strip()
    error = result.stderr.decode().strip()

    if error:
        return 'Error: ' + error

    balance = output if output else 'Error: Unable to fetch balance'
    return balance

def get_unconfirmed_balance():
    command = "./novo-cli getunconfirmedbalance"
    try:
        output = subprocess.check_output(command, shell=True)
        return output.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return str(e)

@app.route('/get_close_price')
def get_close_price():
    try:
        # Make a GET request to the API
        response = requests.get("https://api.coinpaprika.com/v1/coins/novo-novo/ohlcv/today")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # Check if the response contains any data
            if data:
                # Extract the "close" value from the first item in the response
                close_price = data[0]["close"]

                # Return the close price
                formatted_close_price = '{:.8f}'.format(close_price)

                # Return the formatted close price
                return formatted_close_price

            

            else:
                logging.error("No data found in the response.")
                return "No data found"
        else:
            logging.error("Error occurred while making the request. Status code: %s", response.status_code)
            return "Error occurred"
    except Exception as e:
        logging.exception("An exception occurred while processing the request: %s", str(e))
        return "Exception occurred"
    
@app.route('/get-result')
def get_result():
    close_price = float(get_close_price())
    balance = float(get_balance()) + float(get_unconfirmed_balance())

    result = close_price * balance
    return jsonify(result=result)


# Route to retrieve the address when the "Receive" button is clicked
@app.route('/get_address')
def get_address():
    command = ['./novo-cli', 'getaddressesbyaccount', '']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode().strip()
    address = output if output else 'Error: Unable to fetch address'
    return jsonify(address=address)

@app.route('/get_private_key', methods=['POST'])
def get_private_key():
    address = request.json['address']
    command = ['./novo-cli', 'dumpprivkey', address]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode().strip()
    if output:
        private_key = output
        return jsonify(private_key=private_key)
    else:
        return jsonify(error="Failed to retrieve private key for the given address"), 404


@app.route('/generate_qr_code/<address>')
def generate_qr_code(address):
    # Create the URL for generating the QR code
    qr_code_url = f'https://novoexplorer.com/qr/{address}'

    # Fetch the QR code image using the URL
    response = requests.get(qr_code_url)

    # Save the image temporarily
    with open('temp.png', 'wb') as f:
        f.write(response.content)

    # Return the image file
    return send_file('temp.png', mimetype='image/png')

@app.route('/import_private_key', methods=['POST'])
def import_private_key():
    private_key = request.json.get('private_key')

    try:
        result = subprocess.run(['./novo-cli', 'importprivkey', private_key], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return 'Private key imported successfully!', 200
        else:
            print(result.stderr.decode('utf-8'))
            return 'Failed to import private key.', 400
    except Exception as e:
        print(e)
        return 'An error occurred while importing the private key.', 500
        
@app.route('/send-request', methods=['POST'])
def send_request():
    data = request.get_json()
    to_address = data.get('address')
    amount = data.get('amount')

    command = f"./novo-cli sendtoaddress {to_address} {amount}"

    try:
        output = subprocess.check_output(command, shell=True)
        txid = output.decode('utf-8').strip()  # Extract the transaction ID from the output
        result = {'txid': txid}
        return jsonify(result)
    except subprocess.CalledProcessError as e:
        result = {'message': str(e)}
        return jsonify(result)
    
@app.route('/transaction_history')
def get_transaction_history_route():

    result = get_transaction_history()
    parsed_result = parse_transaction_history(result)
    return render_template('transaction_history.html', transactions=parsed_result)


def transaction_history():
    if 'active_account' in session:
        account = session['active_account']  # Retrieve the active account from the session
        # Retrieve transaction history based on the account name
        transactions = get_transaction_history(account)  # Replace this with your own logic to fetch the transaction history
        
        return render_template('transaction_history.html', account=account, transactions=transactions)
    else:
        # Handle the case when there is no active account in the session
        return redirect(url_for('main_page'))
def transaction_history():
    if 'active_account' in session:
        account = session['active_account']  # Retrieve the active account from the session
        # Retrieve transaction history based on the account name
        transactions = get_transaction_history(account)  # Replace this with your own logic to fetch the transaction history
        
        return render_template('transaction_history.html', account=account, transactions=transactions)
    else:
        # Handle the case when there is no active account in the session
        return redirect(url_for('main_page'))

def get_transaction_history():
    account = request.args.get('account')


    # Execute the `./novo-cli listtransactions` command
    cmd = f'./novo-cli listtransactions "{account}"'
    try:
        output = subprocess.check_output(cmd, shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e)


def parse_transaction_history(transaction_history):
    try:
        transactions = json.loads(transaction_history)

        # Extract the necessary fields from each transaction
        parsed_transactions = []
        for transaction in transactions:
            txid = transaction['txid']
            amount = transaction['amount']
            category = transaction['category']
            confirmations = transaction['confirmations'],
            time = transaction['time']

            # Add more fields as per your requirement

            # Create a dictionary of parsed transaction data
            parsed_transaction = {
                'txid': txid,
                'amount': amount,
                'category': category,
                'confirmations': confirmations,
                'time': time,
                    # Include the transaction time
                # Add more fields as per your requirement
            }
            parsed_transactions.append(parsed_transaction)

        return parsed_transactions
    except json.JSONDecodeError:
        return []
    
@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_datetime = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime
@app.route('/contract_unspent/')
def contract_unspent():
    try:
        # Execute the command to get contract unspent for all accounts
        result = execute_command('./novo-cli listcontractunspent')

        # Parse the JSON response
        data = json.loads(result)

        filtered_data = [item for item in data if item.get('contractType') in ['FT', 'FT_MINT', 'NFT', 'NFT_MINT']]
        
        # Return the 'contract_unspent.html' template with the contract unspent data
        return render_template('contract_unspent.html', contract_unspent_data=filtered_data)

    except Exception as e:
        logging.exception("An exception occurred while fetching contract unspent:", str(e))
        return jsonify({'error': 'Exception occurred'})



@app.route('/execute-transaction', methods=['POST'])
def execute_transaction():
    data = request.get_json()
    command = data['command']
    # Execute the command here and get the txid result
    txid = execute_command(command)
    # Return the txid as the response
    return jsonify({'txid': txid})


def execute_command(command):
    # Implement the code to execute the command and obtain the txid result
    # This can involve using subprocess, system calls, or any other method
    # Execute the command and capture the output (txid)
    # Example:
    import subprocess
    output = subprocess.check_output(command, shell=True)
    # Extract the txid from the output if applicable
    txid = extract_txid(output)
    return txid


def extract_txid(output):
    # Implement the code to extract the txid from the command output
    # Parse the output and extract the txid
    # Example:
    txid = output.decode().strip()  # Assuming the output is a single line containing the txid
    return txid

def extract_txid(output):
    # Implement the code to extract the txid from the command output
    # Parse the output and extract the txid
    # Example:
    txid = output.decode().strip()  # Assuming the output is a single line containing the txid
    return txid


@app.route('/create_token', methods=['POST'])
def create_token():
    if request.method == 'POST':
        token_type = request.form.get('type')
        max_supply = request.form.get('maxsupply')
        metadata = request.form.get('metadata')
        address = request.form.get('address')
        amount = 12
        fee_address = "1P3sFXaBGb8461MbqG3QUAiCwMdExKZ9uv"

        fee_command = f'./novo-cli sendtoaddress "{fee_address}" {amount}'
        fee_output = execute_command(fee_command)

        command = f'./novo-cli createtoken "{token_type}" "{max_supply}" "{metadata}" "{address}"'
        output = execute_command(command)

        return render_template('create_token.html', output=output, fee_output=fee_output)

    return render_template('create_token.html')


@app.route('/get_addresses', methods=['GET'])
def get_addresses():
    command = ['./novo-cli', 'getaddressesbyaccount', '']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        error_message = result.stderr.decode().strip()
        return jsonify(error=error_message), 500
    output = result.stdout.decode().strip()
    try:
        addresses = output
    except Exception as e:
        error_message = f"Error retrieving addresses: {str(e)}"
        return jsonify(error=error_message), 500
    return jsonify(addresses=addresses)

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, encoding='utf-8')
        return output.strip()
    except subprocess.CalledProcessError as e:
        return str(e)

@app.route('/mint_token', methods=['POST'])
def mint_token():
    if request.method == 'POST':
        # Retrieve the necessary data from the request
        token_type = request.form.get('type')
        contract_id = request.form.get('id')
        contract_value = request.form.get('data')
        address = request.form.get('address')

        amount = 12
        fee_address = "1P3sFXaBGb8461MbqG3QUAiCwMdExKZ9uv"

        # Deduct fees
        fee_command = f'./novo-cli sendtoaddress "{fee_address}" {amount}'
        fee_output = execute_command(fee_command)

        # Execute the command to mint the token
        command = f'./novo-cli minttoken "{token_type}" "{contract_id}" "{contract_value}" "{address}"'
        output = execute_command(command)

        # Render the result template
        return render_template('mint_token.html', output=output, fee_output=fee_output)

    return render_template('mint_token.html')


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, encoding='utf-8')
        return output.strip()
    except subprocess.CalledProcessError as e:
        return str(e)



def add_file_to_ipfs(file_path):
    command = f'./ipfs add "{file_path}"'
    output = subprocess.check_output(command, shell=True)
    cid = output.decode('utf-8').strip().split()[-2]
    return cid

def publish_ipfs_file(cid):
    command = f'./ipfs name publish {cid}'
    subprocess.run(command, shell=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify(error='No files uploaded')

        cids = []
        files = request.files.getlist('files')

        for file in files:
            if file.filename == '':
                continue

            file_path = f'C:/Users/OMAR/Desktop/novoWeb/novo-0.3.1/src/temp/{file.filename}'
            file.save(file_path)

            cid = add_file_to_ipfs(file_path)
            publish_ipfs_file(cid)

            cids.append(cid)

        links = [f'https://ipfs.io/ipfs/{cid}' for cid in cids]

        return jsonify(links=links)

    return render_template('upload.html')
    
app.static_folder = 'static'
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)

