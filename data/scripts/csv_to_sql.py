import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path


db_url = "postgresql://neondb_owner:npg_hgMT6X1KNUBa@ep-fragrant-sky-a1l6ctkh-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(db_url)


CSV_DIR = Path(__file__).parent.parent.parent / "data"


for file in CSV_DIR.glob("*.csv"):
    print(f"Processing {file}")

    df = pd.read_csv(file)
    df.to_sql(file.stem, engine, if_exists="replace", index=False, schema="public")


print("Done")
