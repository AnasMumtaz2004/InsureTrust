import os
import yaml
from pathlib import Path

agents_dir = Path(r"c:\Users\ANAS MUMTAZ\Desktop\OOPS\InsureTrust\Backend\agents")
for agent_path in agents_dir.iterdir():
    if agent_path.is_dir():
        yaml_file = agent_path / "agent.yaml"
        if yaml_file.exists():
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
            if data:
                if "llm_model" in data:
                    del data["llm_model"]
                if "temperature" in data:
                    del data["temperature"]
                content = yaml.dump(data, sort_keys=False)
                content = "# Model and temperature are set in config.json (llm, agents.<name>)\n" + content
                with open(yaml_file, "w") as f:
                    f.write(content)
