# import_runner.py

import config
from data_importer import import_excel_to_mysql

if __name__ == "__main__":
    try:
        import_excel_to_mysql(
            config.FILE_PATH_1,
            config.SHEET_NAME_1,
            config.TABLE_NAME_1,
            config.EXPECTED_COLUMNS
        )

        import_excel_to_mysql(
            config.FILE_PATH_2,
            config.SHEET_NAME_2,
            config.TABLE_NAME_2,
            config.EXPECTED_COLUMNS
        )

    except Exception as e:
        print(f"❌ Import failed: {e}")