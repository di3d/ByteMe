from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://postgres:iloveESD123@localhost:5433/recommendation_db")
df = pd.read_sql("SELECT * FROM recommendation", engine)
print(df)
