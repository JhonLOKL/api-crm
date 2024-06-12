import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
import re
from datetime import datetime, timedelta

from ..utils.credentials import credentials


def save_register( register ):
    
    try:
        
        user_already_exists = False
        
        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc  = gspread.authorize(credenciales)
        
        url_document = config('CRM_URL')

        document_id = url_document.split("/")[5]

        sheet = gc.open_by_key(document_id)

        sheet_name = "CRM (Oportunidad)"
        sheet_crm = sheet.worksheet(sheet_name)

        data = sheet_crm.get_all_values()[1:]

        crm_oportunidad = pd.DataFrame(data, columns=sheet_crm.get_all_values()[0])
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\+', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\=', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r"\'", "", regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace("'", "")
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace('+', '')
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace('=', '')
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\(.*?\)', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'^57', '', regex=True)
        
        phone_to_check = ''
        if register.get('phone'):
            phone_to_check = register.get('phone')
            phone_to_check = re.sub(r'\(.*?\)', '', phone_to_check)
            phone_to_check = phone_to_check.replace('+', '')
            phone_to_check = phone_to_check.replace("'", "")
            phone_to_check = phone_to_check.replace('=', '')
            phone_to_check = phone_to_check.replace('-', '')

            if phone_to_check.startswith('57'):
                phone_to_check = phone_to_check[2:]

        if ('email' in register) and register['email'] != "":
            email_to_check = register['email']
            user_already_exists = email_to_check in crm_oportunidad['Email'].values

        if (user_already_exists == False) and ('phone' in register) and (register['phone'] != ""):
            user_already_exists = phone_to_check in crm_oportunidad['Celular'].values

        if (user_already_exists == False):
            spreadsheet = gc.open_by_url(config('CRM_URL'))
            
            if not register:
                register['phone'] = ''
            if not register.get('email'):
                register['email'] = ''    
            
            now = datetime.now() - timedelta(hours=5)
            

            df = pd.DataFrame({
                'Nombre': [register.get('firstName')],
                'Apellido': [register.get('lastName')],
                'Celular': [register['countryPhoneCode'] + register['phone']],
                'Email': [register.get('email')],
                "Como nos conocio" : [register.get('leadOrigin')],
                'Origen': "Registro pag web",
                'Proyecto': [""],
                'Fecha ingreso': [now.strftime("%d/%m/%Y")],
                'Hora Ingreso': [now.strftime("%H:%M")]
            })
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
        return "Error guardando el registro en CRM"
 
