from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
import json
from datetime import datetime
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING')
database = os.getenv('DATABASE')
collection_name = os.getenv('COLLECTION')
# MIEL : https://alimentos.cba.gov.ar/#/publico/productos

def get_main_link():
    service = Service(executable_path=r"C:\chromedriver-win64\chromedriver.exe")   
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9030")
    driver = webdriver.Chrome(service=service, options=options)

    output = []
    for i in range(1, 10):
        print(f"------- Page {i} -------")
        tbody_list = driver.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
        
        for item in tbody_list:
            rnpa = item.find_element(By.CLASS_NAME, 'cdk-column-NumeroRNPA').text
            print(f'RNPA : {rnpa}')
            
            denominación = item.find_element(By.CLASS_NAME, 'cdk-column-Denominacion').text
            print(f'Denomination : {denominación}')

            nombreDeFantasía = item.find_element(By.CLASS_NAME, 'cdk-column-NombreFantasia').text
            print(f'Fantasty Name : {nombreDeFantasía}')
            if nombreDeFantasía == "-":
                nombreDeFantasía = ""

            marca = item.find_element(By.CLASS_NAME, 'cdk-column-Marca').text
            print(f'Brand : {marca}')

            razon_social = item.find_element(By.CLASS_NAME, 'cdk-column-RazonSocial').text
            print(f"Razon Social : {razon_social}")

            cuit = item.find_element(By.CLASS_NAME, 'cdk-column-CuitFirmaProp').text
            print(f'CUIT : {cuit}')

            output.append({
                "rnpa": rnpa,
                "rne": "",
                "denominación": denominación,
                "marca": marca,
                "nombreDeFantasía": nombreDeFantasía,
                "origenDelProducto": "",
                "firm": {
                    "razonSocial": razon_social,
                    "cuit": cuit,
                    "domicilio": ""
                },
                "establishment": {
                    "fraccionadoPor": "",
                    "rne": "",
                    "domicilio": ""
                },
                "rneInfo": {
                    "propietario": "",
                    "establecimiento": "",
                    "domicilio": "",
                    "localidad": "",
                    "otorgado": "",
                    "vencimiento": ""
                },
                "createdAt": "",
                "updatedAt": "",
                "__v": "",
                "matchCount": "",
                "vencimiento": '',
                "date" : ""
            })

        with open('output.json', 'w') as data:
            json.dump(output, data, indent=4)

        print(len(output))
        
        next_button = driver.find_element(By.CLASS_NAME, 'mat-paginator-navigation-next')
        driver.execute_script('arguments[0].click();', next_button)
        sleep(5)
    
    return output


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
        item["vencimiento"] = datetime.now()
        item["rneInfo"]["vencimiento"] = item["vencimiento"]
        item["rneInfo"]["otorgado"] = item["vencimiento"]
        item["createdAt"] = datetime.now()
        item["updatedAt"] = datetime.now()
        item["matchCount"] = 0

    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]

    insert_data = collection.insert_many(json_data)
    # print(f"Inserted document ID : {insert_data.inserted_ids}")
    print(f"Total number of inserted document : {len(insert_data.inserted_ids)}")
    print(f"Total number of documents in the collection : {collection.count_documents({})}")


if __name__ == "__main__":
    # json_data = get_main_link()

    with open("output.json", "r") as data:
        json_data = json.load(data)
    
    for item in json_data:
        if "-" in item["rnpa"]:
            item["rnpa"] = item["rnpa"].replace("-", "")

        if "-" in item["rne"]:
            item["rne"] = item["rne"].replace("-", "")
            
    # read_data_database()
    # get_database_collection_database()
    # delete_data_database()
    insert_data_mongodb(json_data)