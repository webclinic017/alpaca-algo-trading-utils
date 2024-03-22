# alpaca-algo-trading-utils


#### Description
```
This is a collection of commonly used features of the Alpaca trading API.
See src folder for code.
```


#### Setup & Usage
```
git clone https://github.com/alpaca-trade-api/alpaca-algo-trading-utils.git
cd alpaca-algo-trading-utils/src
python3 -m venv virt_env
. virt_env/bin/activate
pip install -r requirements.txt
cp credentials_template.json credentials.json
# put API keys from Alpaca Web App into credentials.json
# run any of the scripts in src folder, example:
python3 get_account_details.py
```

