from app import app, db
from sqlalchemy import inspect

with app.app_context():

    inspector = inspect(db.engine)

    print("\nHIRESENSE AI - DATABASE SCHEMA VERIFICATION\n")

    for table_name, model_table in db.metadata.tables.items():

        if not inspector.has_table(table_name):
            print(f"❌ Missing table: {table_name}")
            continue

        actual_columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }

        model_columns = {
            column.name
            for column in model_table.columns
        }

        missing = model_columns - actual_columns
        extra = actual_columns - model_columns

        if not missing and not extra:
            print(f"✅ {table_name}: All columns match")
        else:
            print(f"❌ {table_name}")
            print("Missing in MySQL:", missing)
            print("Extra in MySQL:", extra)

    print("\nSchema verification completed.")