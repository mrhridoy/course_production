def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "Welcome to ICT Bangladesh API"


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
