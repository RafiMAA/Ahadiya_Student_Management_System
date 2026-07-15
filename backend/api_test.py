import urllib.request
import json
from app.config import get_settings
import asyncpg
import asyncio

async def main():
    s = get_settings()
    
    import jwt
    import datetime
    token = jwt.encode({
        "sub": "admin",
        "role": "Admin",
        "id": "11111111-1111-1111-1111-111111111111",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, s.jwt_secret, algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    req = urllib.request.Request("http://localhost:8000/academic-years/current", headers=headers)
    with urllib.request.urlopen(req) as response:
        print("GET current:", json.loads(response.read().decode()))
        
    req2 = urllib.request.Request("http://localhost:8000/academic-years/current/label", headers=headers, data=json.dumps({"year_label": "2029"}).encode(), method="PATCH")
    with urllib.request.urlopen(req2) as response:
        print("PATCH current:", json.loads(response.read().decode()))

asyncio.run(main())
