from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
import json
from datetime import datetime
import uuid
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING')
database = os.getenv('DATABASE')
collection_name = os.getenv('COLLECTION')

def get_main_link():
    service = Service(executable_path=r"C:\chromedriver-win64\chromedriver.exe")   
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9030")
    driver = webdriver.Chrome(service=service, options=options)

    tbody_list = driver.find_element(By.ID, 'table-result2').find_elements(By.TAG_NAME, 'tbody')
    
    output = []
    for tbody in tbody_list:
        tr_list = tbody.find_elements(By.TAG_NAME, 'tr')
        for tr in tr_list:
            sub_link = tr.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f'Sub Link : {sub_link}')

            rnpa = tr.find_element(By.TAG_NAME, 'a').text
            print(f'RNPA : {rnpa}')
            
            td_list = tr.find_elements(By.TAG_NAME, 'td')
            
            denomination = td_list[1].text
            print(f'Denomination : {denomination}')

            fantasty_name = td_list[2].text
            print(f'Fantasty Name : {fantasty_name}')

            brand = td_list[3].text
            print(f'Brand : {brand}')

            headline = td_list[4].text
            print(f'Headline : {headline}')

            state = td_list[5].text
            print(f'State : {state}')

            output.append({"link" : sub_link,
                        "rnpa" : rnpa,
                        "denomination" : denomination,
                        "fantastyName" : fantasty_name,
                        "brand" : brand,
                        "headline" : headline,
                        "state" : state})
    
    print(len(output))
    
    with open('output.json', 'w') as data:
        json.dump(output, data, indent=4)
    
    return output, driver


def extract_sub_link(sub_links):
    final_result = []
    for item_index, item in enumerate(sub_links, start=1):
        print(f"\n-------------- Print {item_index} --------------\n")
        driver = webdriver.Chrome()
        driver.get(item['link'])
        sleep(1)

        wait = WebDriverWait(driver, 10)
        frame = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'frame1')))

        while True:
            try:
                form = driver.find_element(By.TAG_NAME, 'form')
                break
            except:
                print("Browser error occured. Refreshing ......")
                driver.refresh()

        rnpa = item['rnpa']
        rne = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[0].text
        print(f'RNE : {rne}')
        denominación = item['denomination']
        marca = item['brand']
        nombreDeFantasía = item['fantastyName']

        origenDelProducto = ''
        # razon_social = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[1].text
        razon_social = ''

        cuit = form.find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, 'tr')[0].find_elements(By.TAG_NAME, 'td')[1].text
        print(f'CUIT : {cuit}')
        firm_domicilio = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[4].text + ", " + form.find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[1].text
        print(f'Firm Domicilio : {firm_domicilio}')

        establishment_fraccionadoPor = ''
        establishment_rne = ''
        establishment_domicilio = ''

        h2_list = form.find_elements(By.TAG_NAME, 'h2')
        for h2 in h2_list:
            if 'Fecha de Vencimiento' in h2.text:
                # vencimiento_date = datetime.strptime(h2.text.split(': ')[-1] + " 00:00:00.000", "%d/%m/%Y %H:%M:%S.%f").isoformat(timespec='milliseconds')
                vencimiento_date = h2.text.split(': ')[-1]
                print(f'veniciento date : {vencimiento_date}')
        
        rneInfo_propietario = ''
        rneInfo_establecimiento = ''
        rneInfo_domicilio = ''
        rneInfo_localidad = ''
        rneInfo_otorgado_date = ''
        rneInfo_veniciento_date = ''

        createdAt = ''
        updatedAt = ''
        __v = ''
        matchCount = ''

        final_result.append({
            "rnpa": rnpa,
            "rne": rne,
            "denominación": denominación,
            "marca": marca,
            "nombreDeFantasía": nombreDeFantasía,
            "origenDelProducto": origenDelProducto,
            "firm": {
                "razonSocial": razon_social,
                "cuit": cuit,
                "domicilio": firm_domicilio
            },
            "establishment": {
                "fraccionadoPor": establishment_fraccionadoPor,
                "rne": establishment_rne,
                "domicilio": establishment_domicilio
            },
            "rneInfo": {
                "propietario": rneInfo_propietario,
                "establecimiento": rneInfo_establecimiento,
                "domicilio": rneInfo_domicilio,
                "localidad": rneInfo_localidad,
                "otorgado": rneInfo_otorgado_date,
                "vencimiento": rneInfo_veniciento_date
            },
            "createdAt": createdAt,
            "updatedAt": updatedAt,
            "__v": __v,
            "matchCount": matchCount,
            "vencimiento": '',
            "date" : vencimiento_date
        })

        with open('db_json.json', 'w') as data:
            json.dump(final_result, data, indent=4)
        
        driver.quit()
    
    print('Generate JSON file for inserting to MongoDB.')
    
    return final_result


def delete_data_database():
    confirm = input("Do you want to delete all the data on your database?(Y/N) : ")
    if confirm == "Y":
        client = MongoClient(connection_string)
        db = client[database]
        collection = db[collection_name]

        delete_result = collection.delete_many({})
        print(f"Number of documents deleted: {delete_result.deleted_count}")
    else:
        pass


def read_data_database():
    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]

    documents = collection.find()
    for doc in documents:
        print(doc)


def get_database_collection_database():
    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]
    
    document_count = collection.count_documents({})

    print(f"Database : {client.list_database_names()}")
    print(f"Collection : {db.list_collection_names()}")
    print(f"Total number of documents in the collection : {document_count}")


def insert_data_mongodb(json_data):
    for item in json_data:
        # Testing
        # item['vencimiento'] = datetime.strptime(item['veniciento'], '%Y-%m-%dT%H:%M:%S')
        # item['rneInfo']['vencimiento'] = datetime.strptime(item['veniciento'], '%Y-%m-%dT%H:%M:%S')
        # item['rneInfo']['otorgado'] = datetime.strptime(item['veniciento'], '%Y-%m-%dT%H:%M:%S')
        # item['createdAt'] = datetime.now()
        # item['updatedAt'] = datetime.now()
        # item['matchCount'] = 0
        # del item['veniciento']
        # del item['rneInfo']['veniciento']

        # Product
        item['firm']['razonSocial'] = datetime.now()
        item['vencimiento'] = datetime.strptime(item['date'], '%d/%m/%Y')
        item['rneInfo']['vencimiento'] = item['vencimiento']
        item['rneInfo']['otorgado'] = item['vencimiento']
        item['createdAt'] = datetime.now()
        item['updatedAt'] = datetime.now()
        item['matchCount'] = 0
        del item['date']

    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]

    insert_data = collection.insert_many(json_data)
    # print(f"Inserted document ID : {insert_data.inserted_ids}")
    print(f"Total number of inserted document : {len(insert_data.inserted_ids)}")
    print(f"Total number of documents in the collection : {collection.count_documents({})}")

if __name__ == "__main__":
    with open('output.json') as data:
        sub_links = json.load(data)
    print(len(sub_links))
    json_data = extract_sub_link(sub_links)

    # read_data_database()
    # get_database_collection_database()
    delete_data_database()
    insert_data_mongodb(json_data)
