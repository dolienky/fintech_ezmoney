# Table of contents
1. [Introduction](#introduction)
2. [Installation](#installation)
    1. [Truffle](#truffle)
    2. [Ganache](#ganache)
    3. [Flask](#flask)
    4. [Web3](#web3)
3. [Instruction](#instruction)

# 1. Introduction <a name="introduction"></a>
This repository demonstrates an MVP (Minimum Viable Product) of a P2P Lending Platform based on blockchain technology. It is developed as a part of the FinTech courses in Erasmus University Rotterdam - School of Management. The course highlights the importance of applying modern techniques to improve challenges in the finance sectors. Overall, this MVP uses the following tools: 

Key Tools Utilized:

**Truffle and Ganache:** These are Node.js-based tools used for simulating the Ethereum blockchain environment. They facilitate smart contract development, testing, and deployment without incurring actual blockchain costs.

**Flask:** A lightweight Python web framework utilized to render a local HTML user interface. Flask handles backend operations and serves as the intermediary between the frontend UI and blockchain interactions.

**Web3:** Used in the backend to establish interactions between the Flask-powered backend and the Ethereum blockchain. Web3 enables transaction execution, smart contract interactions, and data retrieval.

The project aims to showcase the feasibility and functionality of a blockchain-powered P2P lending platform. It emphasizes practical implementation and demonstration of blockchain technology's potential in financial applications, focusing on security, transparency, and efficiency enhancements.

# 2. Installation <a name="installation"></a>
The installation instruction is based on the author's operating system Windows 11 Home Version 21H2. Here the term **terminal** refers to the built-in Command Prompt or equivalently, the terminal of any compilers (Spyder, VSCode, PyCharm, etc.).

In most cases, commands have to be executed in the same directory as the file. For example, to move from the root directory with the form of *C:\Users* to the Desktop directory *C:\Users\Desktop*, type the following:
```
cd Desktop
```
To return to the parent directory, use:
```
cd ..
```

## 2.1 Truffle <a name="truffle"></a>
Truffle is a development framework for Ethereum. It requires Node.js and npm (Node Package Manager) to be installed. Download and install Node.js from [nodejs.org](https://nodejs.org/).

Then Truffle can be installed globally by typing the following into the **terminal**:
```
npm install -g truffle
```
The installation can be verified by checking the version through the **terminal**:
```
truffle version
```

## 2.2 Ganache <a name="ganache"></a>
Ganache is a personal blockchain for Ethereum development that runs locally on your PC. It simulates an Ethereum network environment without the need for real Ether, making it ideal for development and testing purposes. Follow the official instruction to download and install Ganache from [Ganache](https://archive.trufflesuite.com/ganache/).

## 2.3 Flask <a name="flask"></a>
Flask is a lightweight web framework for Python, ideal for building web applications. Open your terminal and install Flask using pip.
```
pip install flask
```
If wanted, Flask installation can be verified by creating a simple Flask app and running it.
Create a Python script *app.py* with the following structure:
```
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```
Run the above script. Then type in the **terminal** (at same directory as *app.py*):
```
python app.py
```
Then open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000). You should see a page with "Hello, World!".

## 2.4 Web3 <a name="web3"></a>
Web3.py is a Python library for interacting with Ethereum. Use pip to install web3 as follows:
```
pip install web3
```
If wanted, the installation can be verified by checking the version in a Python terminal or script
```
import web3
print(web3.__version__)
```
# 3. Instruction <a name="instruction"></a>
