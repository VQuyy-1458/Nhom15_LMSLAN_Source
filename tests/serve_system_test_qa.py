"""Use the generated full-system dataset with the existing browser layout audit."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["CSS_DATA_ROOT"] = os.environ.get("CSS_UI_QA_ROOT", str(ROOT / "sample-data" / "full-system"))

from app import config, main, storage
from app.runtime import data_lease
from app.security import new_session
from scripts.seed_system_test import verify

with data_lease(config.DATA_DIR):
    storage.initialize()
    verify(Path(os.environ["CSS_DATA_ROOT"]))
    manifest = json.loads((Path(os.environ["CSS_DATA_ROOT"]) / "manifest.json").read_text(encoding="utf-8"))
    main.Handler.log_message = lambda *args: None
    server = main.ThreadingHTTPServer(("127.0.0.1", 0), main.Handler)
    server.daemon_threads = True
    fixture = {"port": server.server_port, "course": manifest["network_course"],
               "student": new_session("DEMO001", "student", "127.0.0.1", "full-system-qa"),
               "admin": new_session("testadmin", "admin", "127.0.0.1", "full-system-qa")}
    print("QA_READY " + json.dumps(fixture), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
