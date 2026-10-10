"""Testes do provador sem PostgreSQL e sem custo.

Usam o provedor SIMULADO e um servidor falso no lugar da OpenAI. Nenhuma chamada paga é feita.
Execute da pasta backend:  python -m pytest tests/test_studio.py   (ou)   python -m unittest tests.test_studio
"""
from __future__ import annotations

import io
import json
import os
import socket
import tempfile
import threading
import time
import unittest
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

TMP = tempfile.mkdtemp(prefix="vesteia-test-")
os.environ.update({"DATABASE_ENABLED": "false", "AI_USAGE_DB": os.path.join(TMP, "usage.sqlite3"),
                   "AVATAR_PROVIDER": "mock", "TRYON_PROVIDER": "mock", "AI_SESSION_LIMIT": "50",
                   "AI_DAILY_LIMIT_LOCAL": "500", "AI_SESSIONS_PER_IP_DAILY": "500",
                   "CORS_ORIGINS": "http://localhost:5173"})
os.environ.pop("OPENAI_API_KEY", None)

import uvicorn  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from app.main import app  # noqa: E402
from app.studio import usage as usage_module  # noqa: E402


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = free_port()
BASE = f"http://127.0.0.1:{PORT}"


_SERVER = None


def start_server():
    global _SERVER
    if _SERVER is not None:
        return _SERVER
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        try:
            urlopen(BASE + "/health", timeout=1)
            _SERVER = server
            return server
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("servidor não iniciou")


def image_bytes(size=(600, 1200), color=(90, 120, 200), fmt="JPEG", exif_orientation=None) -> bytes:
    image = Image.new("RGB", size, (235, 235, 235))
    draw = ImageDraw.Draw(image)
    w, h = size
    draw.ellipse([w * .4, h * .05, w * .6, h * .18], fill=(200, 160, 130))
    draw.rectangle([w * .3, h * .2, w * .7, h * .55], fill=color)
    draw.rectangle([w * .33, h * .55, w * .67, h * .95], fill=(40, 40, 50))
    out = io.BytesIO()
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        image.save(out, format=fmt, exif=exif)
    else:
        image.save(out, format=fmt)
    return out.getvalue()


def garment_bytes(color=(20, 20, 20)) -> bytes:
    image = Image.new("RGB", (512, 512), (255, 255, 255))
    ImageDraw.Draw(image).polygon([(130, 90), (380, 90), (470, 170), (400, 230), (380, 200), (380, 470), (130, 470),
                                   (130, 200), (110, 230), (40, 170)], fill=color)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def call(method, path, *, token=None, fields=None, files=None, headers=None):
    headers = dict(headers or {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if fields is not None or files is not None:
        boundary = "b" + uuid.uuid4().hex
        parts = []
        for name, value in (fields or {}).items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        for name, filename, content, ctype in (files or []):
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                         f"Content-Type: {ctype}\r\n\r\n".encode() + content + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif method == "POST":
        body = b""
    request = Request(BASE + path, data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read()
            return response.status, (json.loads(raw) if raw else None)
    except HTTPError as error:
        raw = error.read()
        return error.code, (json.loads(raw) if raw else None)


def rid() -> str:
    return uuid.uuid4().hex[:16]


class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = start_server()

    def setUp(self):
        os.environ.update({"AVATAR_PROVIDER": "mock", "TRYON_PROVIDER": "mock", "AI_SESSION_LIMIT": "50"})
        status, data = call("POST", "/api/studio/session", fields={})
        self.assertEqual(status, 200, data)
        self.token = data["token"]

    # ---- inicialização sem banco -------------------------------------------------------------
    def test_starts_without_database_and_has_no_catalog(self):
        status, data = call("GET", "/health")
        self.assertEqual((status, data["database_enabled"]), (200, False))
        self.assertEqual(call("GET", "/mvp/catalogo")[0], 404)
        status, data = call("GET", "/api/studio/status")
        self.assertEqual(status, 200)
        self.assertEqual(data["tryon"]["id"], "mock")
        self.assertTrue(data["tryon"]["ready"])
        self.assertNotIn("produtos", json.dumps(data))

    def test_requires_session(self):
        status, data = call("POST", "/api/studio/photo/check", fields={"framing": "rosto"},
                            files=[("photo", "a.jpg", image_bytes(), "image/jpeg")])
        self.assertEqual(status, 401)
        self.assertIn("Sessão", data["detail"])

    def test_rejects_foreign_origin(self):
        status, _ = call("POST", "/api/studio/session", fields={}, headers={"Origin": "https://malicioso.example"})
        self.assertEqual(status, 403)

    # ---- validação de arquivos --------------------------------------------------------------
    def test_upload_validation(self):
        bad = call("POST", "/api/studio/photo/check", token=self.token, fields={"framing": "corpo_inteiro"},
                   files=[("photo", "x.jpg", b"isto nao e imagem" * 40, "image/jpeg")])
        self.assertEqual(bad[0], 415)
        tiny = call("POST", "/api/studio/photo/check", token=self.token, fields={"framing": "corpo_inteiro"},
                    files=[("photo", "x.png", image_bytes((100, 120), fmt="PNG"), "image/png")])
        self.assertEqual(tiny[0], 422)
        gif = io.BytesIO()
        Image.new("RGB", (400, 400)).save(gif, format="GIF")
        self.assertEqual(call("POST", "/api/studio/photo/check", token=self.token, fields={"framing": "rosto"},
                              files=[("photo", "x.gif", gif.getvalue(), "image/gif")])[0], 415)
        webp = call("POST", "/api/studio/photo/check", token=self.token, fields={"framing": "corpo_inteiro"},
                    files=[("photo", "x.webp", image_bytes(fmt="WEBP"), "image/webp")])
        self.assertEqual(webp[0], 200, webp)

    def test_exif_orientation_is_respected(self):
        status, data = call("POST", "/api/studio/photo/check", token=self.token, fields={"framing": "corpo_inteiro"},
                            files=[("photo", "r.jpg", image_bytes((1200, 600), exif_orientation=6), "image/jpeg")])
        self.assertEqual(status, 200, data)
        self.assertEqual((data["width"], data["height"]), (600, 1200))

    # ---- avatar ------------------------------------------------------------------------------
    def avatar(self, **overrides):
        fields = {"framing": "meio_corpo", "upper_state": "sem_camiseta", "consent": "true",
                  "request_id": rid(), "expected_calls": "1"}
        fields.update(overrides)
        return call("POST", "/api/studio/avatar", token=self.token, fields=fields,
                    files=[("photo", "p.jpg", image_bytes(), "image/jpeg")])

    def test_avatar_guards(self):
        self.assertEqual(self.avatar(consent="false")[0], 422)
        status, data = self.avatar(expected_calls="3")
        self.assertEqual(status, 409)
        self.assertIn("1 geração", data["detail"])
        same = rid()
        first = self.avatar(request_id=same)
        self.assertEqual(first[0], 200, first)
        self.assertTrue(first[1]["simulated"])
        self.assertTrue(first[1]["estimated_regions"])
        self.assertTrue(first[1]["image"].startswith("data:image/jpeg;base64,"))
        repeated = self.avatar(request_id=same)
        self.assertEqual(repeated[0], 409)
        self.assertIn("repetida", repeated[1]["detail"])

    def test_photo_avatar_needs_full_body_and_does_not_stretch(self):
        os.environ["AVATAR_PROVIDER"] = "photo"
        status, data = self.avatar(framing="rosto", expected_calls="0")
        self.assertEqual(status, 422)
        status, data = self.avatar(framing="corpo_inteiro", expected_calls="0")
        self.assertEqual(status, 200, data)
        self.assertEqual((data["width"], data["height"], data["calls"]), (1024, 1536, 0))
        self.assertFalse(data["simulated"])

    # ---- prova e look -----------------------------------------------------------------------------
    def tryon(self, metas, expected="1"):
        files = [("base", "b.jpg", image_bytes((1024, 1536)), "image/jpeg")]
        files += [("garments", f"g{i}.png", garment_bytes(), "image/png") for i, _ in enumerate(metas)]
        return call("POST", "/api/studio/tryon", token=self.token, files=files,
                    fields={"garments_meta": json.dumps(metas), "consent": "true", "request_id": rid(),
                            "expected_calls": expected})

    def test_tryon_and_look_rules(self):
        status, data = self.tryon([{"category": "camiseta", "size_label": "M"}])
        self.assertEqual(status, 200, data)
        self.assertEqual(data["garments"][0]["slot"], "upper")
        status, data = self.tryon([{"category": "camiseta"}, {"category": "calca"}])
        self.assertEqual(status, 200, data)
        self.assertEqual([g["slot"] for g in data["garments"]], ["lower", "upper"])
        self.assertEqual(self.tryon([{"category": "camiseta"}, {"category": "camisa"}])[0], 422)
        self.assertEqual(self.tryon([{"category": "vestido"}, {"category": "calca"}])[0], 422)
        self.assertEqual(self.tryon([{"category": "inexistente"}])[0], 422)

    def test_session_lock_blocks_parallel_generation(self):
        from app.studio.sessions import STORE
        session = STORE.get(self.token)
        session.lock.acquire()
        try:
            status, data = self.tryon([{"category": "camiseta"}])
        finally:
            session.lock.release()
        self.assertEqual(status, 409)
        self.assertIn("andamento", data["detail"])

    # ---- tamanhos ----------------------------------------------------------------------------
    def sizes(self, sizes, expected=None, selected="M"):
        return call("POST", "/api/studio/size-previews", token=self.token,
                    files=[("base", "b.jpg", image_bytes((1024, 1536)), "image/jpeg"),
                           ("garment", "g.png", garment_bytes(), "image/png")],
                    fields={"category": "camiseta", "sizes": json.dumps(sizes), "selected_label": selected,
                            "body": json.dumps({"torax_cm": 100}), "consent": "true", "request_id": rid(),
                            "expected_calls": str(expected if expected is not None else len(sizes))})

    def test_size_previews(self):
        missing = self.sizes([{"label": "P", "measures": {}}, {"label": "M", "measures": {"largura_cm": 52}}])
        self.assertEqual(missing[0], 422)
        self.assertIn("Faltam medidas", missing[1]["detail"])
        sizes = [{"label": "P", "measures": {"largura_cm": 48, "comprimento_cm": 68}},
                 {"label": "M", "measures": {"largura_cm": 52, "comprimento_cm": 71}},
                 {"label": "G", "measures": {"largura_cm": 57, "comprimento_cm": 74}}]
        self.assertEqual(self.sizes(sizes, expected=1)[0], 409)
        status, data = self.sizes(sizes)
        self.assertEqual(status, 200, data)
        self.assertEqual([p["label"] for p in data["previews"]], ["P", "M", "G"])
        self.assertTrue(all(p["repeated_of"] is None for p in data["previews"]))
        same = [{"label": "M", "measures": {"largura_cm": 52}}, {"label": "G", "measures": {"largura_cm": 52}}]
        status, data = self.sizes(same)
        self.assertEqual(status, 200, data)
        self.assertEqual(data["previews"][1]["repeated_of"], "M")

    def test_size_previews_refused_for_providers_without_measurements(self):
        os.environ["TRYON_PROVIDER"] = "catvton"
        status, data = self.sizes([{"label": "P", "measures": {"largura_cm": 48}}, {"label": "M", "measures": {"largura_cm": 52}}])
        self.assertEqual(status, 422)
        self.assertIn("comparação de medidas", data["detail"])

    # ---- limites -------------------------------------------------------------------------------
    def test_limits_persist_across_restart(self):
        os.environ["AI_SESSION_LIMIT"] = "2"
        self.assertEqual(self.avatar()[0], 200)
        self.assertEqual(self.avatar()[0], 200)
        status, data = self.avatar()
        self.assertEqual(status, 429)
        self.assertIn("Limite desta sessão", data["detail"])
        # "Reinicialização": descarta o objeto em memória e relê o arquivo SQLite.
        usage_module._LEDGERS.clear()
        from app.config import get_settings
        from app.studio.sessions import STORE
        snap = usage_module.get_ledger(get_settings()).snapshot(get_settings(), STORE.get(self.token).id)
        self.assertEqual(snap["sessao"], 2)
        self.assertGreaterEqual(snap["locais_hoje"], 2)


class FakeOpenAI(BaseHTTPRequestHandler):
    hits: list = []
    mode = "ok"

    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        FakeOpenAI.hits.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        if FakeOpenAI.mode == "error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"x"}}')
            return
        if FakeOpenAI.mode == "badkey":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":{"code":"invalid_api_key"}}')
            return
        import base64
        payload = {"data": [{"b64_json": base64.b64encode(image_bytes((1024, 1536))).decode()}]}
        if FakeOpenAI.mode == "empty":
            payload = {"data": []}
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


class OpenAIProviderTests(unittest.TestCase):
    """Servidor local falso: valida o contrato e os controles de custo sem chamada paga."""

    @classmethod
    def setUpClass(cls):
        cls.server = start_server()
        cls.fake = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAI)
        threading.Thread(target=cls.fake.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.fake.shutdown()
        for key in ("OPENAI_API_KEY", "AI_PAID_ENABLED", "OPENAI_BASE_URL"):
            os.environ.pop(key, None)
        os.environ.update({"AVATAR_PROVIDER": "mock", "TRYON_PROVIDER": "mock"})

    def setUp(self):
        FakeOpenAI.hits.clear()
        FakeOpenAI.mode = "ok"
        os.environ.update({"AVATAR_PROVIDER": "openai", "TRYON_PROVIDER": "openai", "AI_SESSION_LIMIT": "50",
                           "OPENAI_BASE_URL": f"http://127.0.0.1:{self.fake.server_address[1]}/v1",
                           "AI_DAILY_LIMIT_PAID": "100", "AI_TOTAL_LIMIT_PAID": "100"})
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("AI_PAID_ENABLED", None)
        self.token = call("POST", "/api/studio/session", fields={})[1]["token"]

    def avatar(self):
        return call("POST", "/api/studio/avatar", token=self.token,
                    fields={"framing": "rosto", "upper_state": "nao_informado", "consent": "true", "request_id": rid(),
                            "expected_calls": "1"}, files=[("photo", "p.jpg", image_bytes(), "image/jpeg")])

    def test_not_ready_without_key_and_paid_flag(self):
        status = call("GET", "/api/studio/status")[1]
        self.assertFalse(status["avatar"]["ready"])
        self.assertIn("OPENAI_API_KEY", status["avatar"]["message"])
        os.environ["OPENAI_API_KEY"] = "sk-test-falsa-0000000000000000"
        self.assertFalse(call("GET", "/api/studio/status")[1]["avatar"]["ready"])  # falta AI_PAID_ENABLED
        self.assertEqual(self.avatar()[0], 503)
        self.assertEqual(FakeOpenAI.hits, [])

    def test_request_contract_and_no_retry(self):
        os.environ.update({"OPENAI_API_KEY": "sk-test-falsa-0000000000000000", "AI_PAID_ENABLED": "true"})
        status, data = self.avatar()
        self.assertEqual(status, 200, data)
        self.assertFalse(data["simulated"])
        hit = FakeOpenAI.hits[0]
        self.assertEqual(hit["path"], "/v1/images/edits")
        self.assertEqual(hit["body"]["model"], "gpt-image-2")
        self.assertNotIn("input_fidelity", hit["body"])
        self.assertEqual(hit["body"]["size"], "1024x1536")
        self.assertTrue(hit["body"]["images"][0]["image_url"].startswith("data:image/jpeg;base64,"))
        self.assertIn("Never depict nudity", hit["body"]["prompt"])
        # Falha do provedor: exatamente uma requisição, sem repetição automática; cota mantida (pode ter sido cobrada).
        FakeOpenAI.hits.clear()
        FakeOpenAI.mode = "error"
        status, data = self.avatar()
        self.assertEqual(status, 502)
        self.assertEqual(len(FakeOpenAI.hits), 1)
        self.assertEqual(data["charged_calls"], 1)
        # Resposta sem imagem = inconclusiva.
        FakeOpenAI.mode = "empty"
        status, data = self.avatar()
        self.assertEqual(status, 502)
        self.assertTrue(data["inconclusive"])
        # Chave inválida: nada gerado, cota devolvida.
        FakeOpenAI.mode = "badkey"
        status, data = self.avatar()
        self.assertEqual((status, data["charged_calls"]), (503, 0))

    def test_tryon_sends_base_and_all_garments_in_one_call(self):
        os.environ.update({"OPENAI_API_KEY": "sk-test-falsa-0000000000000000", "AI_PAID_ENABLED": "true"})
        files = [("base", "b.jpg", image_bytes((1024, 1536)), "image/jpeg"),
                 ("garments", "a.png", garment_bytes(), "image/png"), ("garments", "b.png", garment_bytes((10, 10, 120)), "image/png")]
        status, data = call("POST", "/api/studio/tryon", token=self.token, files=files,
                            fields={"garments_meta": json.dumps([{"category": "camiseta", "size_label": "M"}, {"category": "calca"}]),
                                    "consent": "true", "request_id": rid(), "expected_calls": "1"})
        self.assertEqual(status, 200, data)
        self.assertEqual(len(FakeOpenAI.hits), 1)
        self.assertEqual(len(FakeOpenAI.hits[0]["body"]["images"]), 3)
        self.assertIn("size M", FakeOpenAI.hits[0]["body"]["prompt"])

    def test_paid_daily_limit(self):
        os.environ.update({"OPENAI_API_KEY": "sk-test-falsa-0000000000000000", "AI_PAID_ENABLED": "true"})
        from app.config import get_settings
        used = usage_module.get_ledger(get_settings()).snapshot(get_settings())["pagas_hoje"]
        os.environ["AI_DAILY_LIMIT_PAID"] = str(used + 1)
        self.assertEqual(self.avatar()[0], 200)
        status, data = self.avatar()
        self.assertEqual(status, 429)
        self.assertIn("diário", data["detail"])
        self.assertEqual(len(FakeOpenAI.hits), 1)


def _is_up() -> bool:
    try:
        urlopen(BASE + "/health", timeout=0.5)
        return True
    except OSError:
        return False


class PureFunctionTests(unittest.TestCase):
    def test_log_redaction(self):
        from app.logging_safe import redact
        text = redact("img data:image/jpeg;base64," + "A" * 500 + " chave sk-abcdefghijklmnopqrstu Bearer abc.def.ghijkl")
        self.assertNotIn("AAAA", text)
        self.assertNotIn("sk-abcdefghijkl", text)
        self.assertNotIn("abc.def", text)

    def test_size_comparison_depends_on_measures(self):
        from app.studio.sizes import compare_size, describe_for_prompt
        self.assertEqual(compare_size("camiseta", {"largura_cm": 52}, {}), [])
        tight = compare_size("camiseta", {"largura_cm": 48}, {"torax_cm": 100})[0]
        self.assertEqual((tight["folga_cm"], tight["leitura"]), (-4.0, "menor que o corpo (tende a apertar)"))
        roomy = compare_size("camiseta", {"largura_cm": 62}, {"torax_cm": 100})[0]
        self.assertEqual(roomy["leitura"], "bem ampla")
        # O mesmo rótulo pode ser justo ou amplo: depende só das medidas.
        self.assertEqual(compare_size("camiseta", {"largura_cm": 62}, {"torax_cm": 124})[0]["leitura"], "justa")
        self.assertIn("not provided", describe_for_prompt("camiseta", "GG", {"largura_cm": 60}, {}))

    def test_compose_look(self):
        from app.studio.categories import compose_look
        self.assertEqual(compose_look(["camiseta", "calca"]), [1, 0])
        self.assertEqual(compose_look(["camiseta", "camisa"]), [1])
        self.assertEqual(compose_look(["camiseta", "calca", "vestido"]), [2])
        self.assertEqual(compose_look(["vestido", "jaqueta"]), [0, 1])


if __name__ == "__main__":
    unittest.main()
