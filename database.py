from sqlalchemy import create_engine

database_engine = create_engine("mysql://service_user:NotSoSecure@database:3306/test_interviu")
