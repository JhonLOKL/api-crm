import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
import re

from ..utils.credentials import credentials

def lead_crm( data ):
    
    try:
        url_documento = config('CRM_URL')
        user_already_exists = False
        
        json_credenciales = credentials()
        
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        print(json_credenciales)
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc  = gspread.authorize(credenciales)
        
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
        if data.get('phone'):
            phone_to_check = data.get('phone')
            phone_to_check = re.sub(r'\(.*?\)', '', phone_to_check)
            phone_to_check = phone_to_check.replace('+', '')
            phone_to_check = phone_to_check.replace("'", "")
            phone_to_check = phone_to_check.replace('=', '')
            phone_to_check = phone_to_check.replace('-', '')

            if phone_to_check.startswith('57'):
                phone_to_check = phone_to_check[2:]

        if (user_already_exists == False) and ('phone' in data) and (data['phone'] != ""):
            user_already_exists = phone_to_check in crm_oportunidad['Celular'].values

        if (user_already_exists == False):
            spreadsheet = gc.open_by_url(config('CRM_URL'))
            
            if not data:
                data['phone'] = ''    
            
            created_at = data.get('createdAt')
            if created_at:
                entry_date = pd.to_datetime(created_at).strftime('%d/%m/%Y')
                entry_time = pd.to_datetime(created_at).strftime('%H:%M')
            else:
                entry_date = None
                entry_time = None

            df = pd.DataFrame({
                'Nombre': [""],
                'Apellido': [""],
                'Celular': [data['phone']],
                'Email': [""],
                "Como nos conocio" : [""],
                'Origen': "Agente IA",
                'Proyecto': ["Nido de Agua"],
                'Fecha ingreso': [entry_date],
                'Hora Ingreso': [entry_time],
                'Fecha Atención' : [entry_date],
                'Hora Atención' : [entry_time],
                'Tiempo Atención' : None,
                'Tiempo en atencion en horas' : None,
                'Estado Oportunidad' : "Interesado",
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
        return "Error guardando el lead desde Laura"
 