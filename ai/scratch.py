import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('ai/.env')
from ai.db.db_access import AIDatabaseAccess
db = AIDatabaseAccess()
print("Using 'active':")
print(db.execute_query("SELECT count(*) FROM policies WHERE agent_id = 'b8626860-7a30-41c2-bad4-e14639f33c45' AND status = 'active';"))
print("Using 'Active':")
print(db.execute_query("SELECT count(*) FROM policies WHERE agent_id = 'b8626860-7a30-41c2-bad4-e14639f33c45' AND status = 'Active';"))
