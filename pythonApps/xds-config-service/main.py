from fastapi import FastAPI, Response
import yaml
import json
import uvicorn
from pathlib import Path
import hashlib

app = FastAPI()

CONFIG_FILE = Path("/app/config.yaml")

def load_config():
    """Load config from file on every call"""
    if not CONFIG_FILE.exists():
        config = {"message": "Hello from Envoy xDS!"}
    else:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {"message": "Hello from Envoy xDS!"}

    # Generate version hash based on config content
    config_str = json.dumps(config, sort_keys=True)
    version = hashlib.md5(config_str.encode()).hexdigest()[:8]

    return config, version

@app.post("/v3/discovery:routes")
async def discovery_routes():
    """Envoy RDS (Route Discovery Service) endpoint"""

    # Read config fresh on every request
    config, version = load_config()
    print(f"Serving config version {version}: {config}")

    route_config = {
        "version_info": version,
        "resources": [
            {
                "@type": "type.googleapis.com/envoy.config.route.v3.RouteConfiguration",
                "name": "local_route",
                "virtual_hosts": [
                    {
                        "name": "direct_response_service",
                        "domains": ["*"],
                        "routes": [
                            {
                                "match": {
                                    "prefix": "/"
                                },
                                "direct_response": {
                                    "status": 200,
                                    "body": {
                                        "inline_string": config.get("message", "Hello from Envoy xDS!")
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

    return route_config

@app.get("/health")
async def health():
    config, version = load_config()
    return {
        "status": "healthy",
        "config_version": version,
        "current_message": config.get("message", "")
    }

@app.get("/")
async def root():
    config, version = load_config()
    return {
        "service": "xDS Config Service",
        "version": version,
        "config": config
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
