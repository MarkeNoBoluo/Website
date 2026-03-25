"""Basic application smoke tests."""


def test_health_check(client):
    """Health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_blog_index(client):
    """Blog index page returns 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_404_page(client):
    """Unknown route returns 404."""
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404


def test_login_page(client):
    """Login page returns 200."""
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_todo_requires_login(client):
    """Todo page redirects unauthenticated users."""
    response = client.get("/todo/")
    assert response.status_code == 302
