import json
from pathlib import Path
from fastapi import FastAPI
import uvicorn
from app.fastapi_microsoft_identity import initialize
from endpoint import helloworld

app = FastAPI()

def configure():
    configure_routing()
    configure_api_keys()

def configure_api_keys():
    file = Path('settings.json').absolute()
    if not file.exists():
        print(f"WARNING: {file} does not exist")
        raise Exception("settings.json not found")
    with open('settings.json') as fin:
        settings = json.load(fin)
        helloworld.api_key = settings.get('api_key')
        configure_auth(settings['tenant_id'], settings['client_id'])

def configure_auth(tenant_id, client_id):
    initialize(tenant_id, client_id)

def configure_routing():
    app.include_router(helloworld.router)

if __name__ == "__main__":
    configure()  # Configure everything
    uvicorn.run(app, host="127.0.0.1", port=8000)
