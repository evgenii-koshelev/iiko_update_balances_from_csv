#https://api-ru.iiko.services/#tag/Customers/paths/~1api~11~1loyalty~1iiko~1customer~1card~1remove/post


from bs4 import BeautifulSoup
import json
import requests, time
import sys
import csv


acc_settings_file = 'acc_settings.txt'

settings = {}
with open(acc_settings_file) as txt:
    for line in txt:
        key, value = line.strip().split(None, 1)
        settings[key] = value.strip()

apiLogin = settings['apiLogin']
organizationId = settings['organizationId']


class Wallet:
    data = {}
    headers = {}
    url= ''
    token = ''
    
    
    def __init__(self):
          self.data = {'apiLogin': apiLogin}
          self.url = 'https://api-ru.iiko.services/api/1/access_token'   #'http://10.0.0.245:80'
          self.session = requests.Session()
          reseived_data = json.loads((self.session.post(self.url, json=self.data)).text)
          #print(reseived_data)
          self.token = reseived_data["token"]
          #print('Токен получен, авторизация успешна')



    def get_guest_info(self, str):
        self.url = 'https://api-ru.iiko.services/api/1/loyalty/iiko/customer/info'
        self.headers = {"Authorization": f'Bearer {self.token}'}
        self.data = {
                'phone': str,
                "type": "phone",
                "organizationId": organizationId
            }
        #return  (self.session.post(self.url, json=self.data, headers=self.headers).text)['walletBalances']
        response = (self.session.post(self.url, json=self.data, headers=self.headers).json())
        return response
        #return(response['walletBalances'][0]['balance'])



    def get_balance(self, str):
        return self.get_guest_info(str)['walletBalances'][0]['balance']
         

         

    def refill_balance(self, phone, summ):
        guest_info = self.get_guest_info(phone)

        #print (type(guest_info))
        #print (guest_info['walletBalances'][0]['id'])
        
        self.url = 'https://api-ru.iiko.services/api/1/loyalty/iiko/customer/wallet/topup'
        self.headers = {"Authorization": f'Bearer {self.token}'}
        self.data = {
                "customerId": guest_info['id'], 
                "walletId": guest_info['walletBalances'][0]['id'], 
                "sum": summ,
                "comment": "string",
                "organizationId": organizationId
                }
        
        if self.session.post(self.url, json=self.data, headers=self.headers).status_code == 200:
            return True
        else:
            return False




    def chargeoff_balance(self, phone, summ):
        guest_info = self.get_guest_info(phone)

        #print (type(guest_info))
        #print (guest_info['walletBalances'][0]['id'])
        
        self.url = 'https://api-ru.iiko.services/api/1/loyalty/iiko/customer/wallet/chargeoff'
        self.headers = {"Authorization": f'Bearer {self.token}'}
        self.data = {
                "customerId": guest_info['id'], 
                "walletId": guest_info['walletBalances'][0]['id'], 
                "sum": summ,
                "comment": "string",
                "organizationId": organizationId
                }
        
        if self.session.post(self.url, json=self.data, headers=self.headers).status_code == 200:
            return True
        else:
            print (self.session.post(self.url, json=self.data, headers=self.headers).text)
            return False





wallet = Wallet()


with open(settings['filename'], newline='\n') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        #print(row)
        print(row['phone'], row['balance'])


        server_balance = wallet.get_balance(row['phone'])
        file_balance = float(row['balance'])
        
        if (server_balance > file_balance): # если на сервере баланс больше, чем в файле, то списываем лишнее
            if  wallet.chargeoff_balance(row['phone'], (server_balance - file_balance)):
                print(f'Balance chargeoff successfully')
                print(f'Current balance is {wallet.get_balance(row["phone"])}')
            else:
                print(f'Balance not chargeoff, error')

        if (server_balance < file_balance):
            if  wallet.refill_balance(row['phone'], (file_balance-server_balance)):
                print(f'Balance inctreased successfully')
                print(f'Current balance is {wallet.get_balance(row["phone"])}')
            else:
                print(f'Balance not inctreased, error')

        if (server_balance == file_balance):
            print('Balance is actual')
        print()
        print()

         
                
                
        
input('Press any key to exit')












    


    
