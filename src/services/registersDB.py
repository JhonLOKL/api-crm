import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
from ..utils.credentials import credentials


def save_register_in_db( register ):
    
    try:
        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc  = gspread.authorize(credenciales)

        spreadsheet = gc.open_by_url(config('DB_URL'))
        sheet_name = "Users"
        worksheet = spreadsheet.worksheet(sheet_name)
            
        df = pd.DataFrame({
            'id': [register.get('id')],
            'email': [register.get('email')],
            'emailVerified': [register.get('emailVerified')],
            'firstName': [register.get('firstName')],
            'lastName': [register.get('lastName')],
            'password': [register.get('password')],
            'leadOrigin': [register.get('leadOrigin')],
            'pageOrigin': [register.get('pageOrigin')],
            'birthDate': [register.get('birthDate')],
            'address': [register.get('address')],
            'state': [register.get('state')],
            'city': [register.get('city')],
            'uniqueCode': [register.get('uniqueCode')],
            'referralCode': [register.get('referralCode')],
            'termsAccepted': [register.get('termsAccepted')],
            'lastLoginAt': [register.get('lastLoginAt')],
            'createdAt': [register.get('createdAt')],
            'updatedAt': [register.get('updatedAt')],
            'deletedAt': [register.get('deletedAt')],
            'roleId': [register.get('roleId')]
        })
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

            return "Usuario agregado correctamente a DB."         
            
        else:
            return "No hay filas vacías para agregar datos."

    except Exception as error:
        print("Se produjo un error:", error)
        return "Error guardando el registro en DB"
 
