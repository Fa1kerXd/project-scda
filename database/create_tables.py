import connection
import tables

if __name__ == "__main__":
    db = connection.main_db()
    # tables.create_table_coordinator(db)
    # tables.create_table_analyst(db)
    # tables.create_table_corrective_patch(db)
    tables.create_table_logging(db)