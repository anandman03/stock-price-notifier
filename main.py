# imports
import ssl
import time
import smtplib
import requests
import argparse
from bs4 import BeautifulSoup
from email.message import EmailMessage


def parse_arguments():
	"""Parser schema to track cmd args
	:returns: parser schema as dictionary
	"""
	parser = argparse.ArgumentParser(description='Stock Details')
	parser.add_argument('--url', required=True, type=str, help='url to be tracked from zerodha')
	parser.add_argument('--target', required=True, type=float, help='target price')
	parser.add_argument('--email', required=True, type=str, help='email for notification')
	parser.add_argument('--pass', required=True, type=str, help='password to login')
	args = parser.parse_args()
	return (args.__dict__)

def fetch_stock_details(request_url):
	"""Performs GET request to supplied URL
	:param request_url: input stock url
	:returns: response object
	"""
	result = requests.get(request_url)
	return result

def extract_price(result):
	"""Extract price from reponse object
	:param result: response object from GET request
	:returns: current price of stock
	"""
	content = BeautifulSoup(result.text, 'html.parser')
	content = content.select_one('.current-price')
	price_string = content.text.split(',')
	price = ''.join(price_string)
	return float(price)

def extract_stock_name(url):
	"""Extract stock name from supplied URL
	:param url: input stock url
	:returns: stock name
	"""
	sub_part = url.split('/')[-1]
	stock_name = sub_part.split('?')[0]
	return stock_name.upper()

def send_email(url, email, password, stock_price, target_price):
	"""Send details as email
	:param url: input stock url
	:param email: user email
	:param password: user password to login
	:param stock_price: current stock price
	:param target_price: target stock price
	:returns: boolean status
	"""
	message = EmailMessage()
	message['From'] = message['To'] = email
	message['subject'] = 'Stock Tracker Update'

	body = f'''
		<html>
			<body>
				<h3>{extract_stock_name(url)}</h3>
				<p>Current Price - Rs {stock_price}</p>
				<p>Target Price - Rs {target_price}</p>
			</body>
		</html>
	'''
	message.add_alternative(body, subtype='html')

	# To establish secure connection
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
		server.login(email, password)
		server.sendmail(email, email, message.as_string())

	return True

def main():
	"""Entry point for the script
	:returns: None
	"""
	args = parse_arguments()

	url, email, password = args['url'], args['email'], args['pass']
	target_price = float(args['target'])

	while True:
		result = fetch_stock_details(url)
		stock_price = extract_price(result)
		if stock_price <= target_price:
			resp = send_email(url, email, password, stock_price, target_price)
			assert resp == True
			return
		else:
			print('Current Price: Rs ' + str(stock_price))
		# Make new request after every 10s
		time.sleep(10)
	return


if __name__ == '__main__':
	main()
