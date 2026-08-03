import ast
import json
import os
from pathlib import Path
from urllib.request import Request


ROOT = Path(__file__).resolve().parent
TREE = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
NOMBRES = {
    "obtener_ollama_api_key",
    "llamar_ollama_cloud",
    "probar_conexion_ollama_cloud",
}


class FakeStreamlit:
    secrets = {"OLLAMA_API_KEY": "clave-de-prueba"}


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({"message": {"content": "CONEXION_OK"}}).encode("utf-8")


captured = {}


def fake_urlopen(request, timeout):
    captured["url"] = request.full_url
    captured["authorization"] = request.headers.get("Authorization")
    captured["payload"] = json.loads(request.data.decode("utf-8"))
    captured["timeout"] = timeout
    return FakeResponse()


nodes = []
for node in TREE.body:
    if isinstance(node, ast.Assign):
        targets = {target.id for target in node.targets if isinstance(target, ast.Name)}
        if targets & {"OLLAMA_CHAT_URL", "OLLAMA_MODEL"}:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in NOMBRES:
        nodes.append(node)

namespace = {
    "json": json,
    "os": os,
    "Request": Request,
    "st": FakeStreamlit(),
    "urlopen": fake_urlopen,
}
exec(compile(ast.Module(body=nodes, type_ignores=[]), "app.py", "exec"), namespace)

assert namespace["probar_conexion_ollama_cloud"]() is True
assert captured["url"] == "https://ollama.com/api/chat"
assert captured["authorization"] == "Bearer clave-de-prueba"
assert captured["payload"]["model"] == "gpt-oss:20b"
assert captured["payload"]["messages"][0]["content"].startswith("Responde solamente")
assert captured["payload"]["stream"] is False
print("ollama cloud client checks ok")
