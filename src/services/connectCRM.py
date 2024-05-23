from flask import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
import re

def save_simulation( simulation ):
    
    try:
        
        user_already_exists = False
        
        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc  = gspread.authorize(credenciales)
        
        url_documento = config('CRM_URL')

        documento_id = url_documento.split("/")[5]

        hoja = gc.open_by_key(documento_id)

        nombre_hoja = "CRM (Oportunidad)"
        hoja_crm = hoja.worksheet(nombre_hoja)

        data = hoja_crm.get_all_values()[1:]

        crm_oportunidad = pd.DataFrame(data, columns=hoja_crm.get_all_values()[0])
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\+', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\=', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r"\'", "", regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace("'", "")
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace('+', '')
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace('=', '')
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\(.*?\)', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'^57', '', regex=True)
        
        phone_to_check = ''
        if simulation.get('phone'):
            phone_to_check = simulation.get('phone')
            phone_to_check = re.sub(r'\(.*?\)', '', phone_to_check)
            phone_to_check = phone_to_check.replace('+', '')
            phone_to_check = phone_to_check.replace("'", "")
            phone_to_check = phone_to_check.replace('=', '')
            phone_to_check = phone_to_check.replace('-', '')

            if phone_to_check.startswith('57'):
                phone_to_check = phone_to_check[2:]
            
            print("---------phone-----------------")
            print(phone_to_check)
        
        if 'email' in simulation:
            email_to_check = simulation['email']
            user_already_exists = email_to_check in crm_oportunidad['Email'].values
        
        if (user_already_exists == False) and ('phone' in simulation):
            user_already_exists = phone_to_check in crm_oportunidad['Celular'].values
            
        if (user_already_exists == False):
            spreadsheet = gc.open_by_url(config('CRM_URL'))
            
            if not simulation:
                simulation['phone'] = ''
            if not simulation.get('email'):
                simulation['email'] = ''    
            
            df = pd.DataFrame({
                'Nombre': [simulation.get('name')],
                'Apellido': [""],
                'Celular': [simulation['phone']],
                'Email': [simulation.get('email')],
                'Origen': simulation.get('leadOrigin'),
                'Proyecto': [""],
                'Fecha ingreso': [pd.to_datetime(simulation.get('createdAt')).strftime('%d/%m/%Y')],
                'Hora Ingreso': [pd.to_datetime(simulation.get('createdAt')).strftime('%H:%M')]
            })
            print(df.head())
            sheet_title = 'CRM (Oportunidad)'
            worksheet = spreadsheet.worksheet(sheet_title)
            empty_rows = [i + 2 for i, row in enumerate(worksheet.get_all_values()[1:]) if not any(row[0:4])]

            if empty_rows:
                columnas_df = df.columns.tolist()
                columnas_hoja = worksheet.row_values(1)
                values = df[columnas_df].values.tolist()

                for row in values:
                    while len(row) < len(columnas_hoja):
                        row.append('')
                        
                for row_index, value_row in zip(empty_rows, values):
                    worksheet.update(f'A{row_index}', [value_row])
                
                return "Usuario agregado correctamente a CRM."         
            
            else:
                return "No hay filas vacías para agregar datos."
        else:
            return "El usuario ya existe, no es necesario agregarlo a CRM."
 
    except Exception as error:
        print("Se produjo un error:", error)
        return "Error guardando la simulacion en CRM"
 
 
def credentials():

    credentials_keys = {
        "type": config('TYPE'),
        "project_id": config('PROJECT_ID'),
        "private_key_id": config('PRIVATE_KEY_ID'),
        "private_key": config('PRIVATE_KEY'),
        "client_email": config('CLIENT_EMAIL'),
        "client_id": config('CLIENT_ID'),
        "auth_uri": config('AUTH_URI'),
        "token_uri": config('TOKEN_URI'),
        "auth_provider_x509_cert_url": config('AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": config('CLIENT_X509_CERT_URL'),
         "universe_domain": config('UNIVERSE_DOMAIN'),
    }

    return credentials_keys