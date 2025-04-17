import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

engine = create_engine(db_url)


CSV_DIR = Path(__file__).parent.parent.parent / "data"


for file in CSV_DIR.glob("*.csv"):
    print(f"Processing {file}")

    df = pd.read_csv(file)
    df.to_sql(file.stem, engine, if_exists="replace", index=False, schema="public")


print("Done")
