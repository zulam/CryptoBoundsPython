import sys
import requests
import time
import smtplib
import config as cfg
from email.message import EmailMessage
from twilio.rest import Client

def send_email(m):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Crypto Bounds'
        msg['From'] = cfg.email['sender']
        msg['To'] = cfg.email['receiver']
        msg.set_content(m)
        smtp_server = "smtp.gmail.com"
        port = 587
        sender = cfg.email['sender']
        password = cfg.email['password']
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    except Exception as e:
        print(e)

def send_text(m):
    account_sid = cfg.service['account_sid']
    auth_token = cfg.service['auth_token']
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=m,
        from_=cfg.service['from'],
        to=cfg.service['to']
    )

ticker = sys.argv[1] 
lower_bound = float(sys.argv[2]) 
upper_bound = float(sys.argv[3])

error_count = 0
threshold_factor = .005
threshold_factor_whole = str(threshold_factor * 100)
upper_threshold = 1 - threshold_factor
lower_threshold = 1 + threshold_factor
lower_adj = lower_bound * lower_threshold
upper_adj = upper_bound * upper_threshold

url = f'https://api.coinbase.com/v2/prices/{ticker}-USD/spot'
message = ""
test_success = True

try:
    test_response = requests.get(url) 
    json = test_response.json()
    price = float(json['data']['amount'])
except:
    send_text('Failure')
    test_success = False

if test_success:
    while True:
        try:
            if error_count >= 10:
                send_text('Mutliple failures')
                error_count = 0
            response = requests.get(url) 
            json = response.json()
            price = float(json['data']['amount'])
            if price <= lower_adj:
                message = f'{ticker}: ${price} is within {threshold_factor_whole} percent of lower bound (${lower_bound}).'
                send_text(message)
                break
            elif price >= upper_adj:
                message = f'{ticker}: ${price} is within within {threshold_factor_whole} percent of upper bound (${upper_bound}).'
                send_text(message)
                break
            else:
                print(str(price))
                time.sleep(10)
        except:
            error_count += 1
            print('Failure')
