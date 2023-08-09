"""
Authentication tests
"""
from rest_framework import status
from rest_framework.reverse import reverse


def get_login_response(
    get_user, get_api_client, extra_user_data=None, assert_status=status.HTTP_200_OK
):
    username = "test@test.com"
    password = "test123"

    data = {
        "username": username,
        "password": password,
    }

    if extra_user_data:
        data.update(extra_user_data)

    user = get_user(**data)
    client = get_api_client()

    url = reverse("auth-login")

    response = client.post(url, data=data, format="json")

    assert response.status_code == assert_status

    return user, client, response


def test_list(get_api_client):
    """
    ensure a GET request doesn't show all users
    """
    client = get_api_client()

    url = reverse("auth-list")

    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # make sure that a logged-in user can't see anything either
    client = get_api_client(create_user=True)

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_login(get_api_client, get_user):
    """
    ensure a cookie is set when logged in
    """
    user, client, response = get_login_response(get_user, get_api_client)
    username = user.username

    result = response.data["result"]
    assert result["username"] == username

    assert response.cookies["auth_token"].value == user.auth_token.key


def test_login_with_mfa(get_api_client, get_user):
    """
    ensure we get an accepted status and no cookie when MFA is enabled for a user
    """
    user, client, response = get_login_response(
        get_user,
        get_api_client,
        extra_user_data=dict(_setup_mfa=True),
        assert_status=status.HTTP_202_ACCEPTED,
    )

    # make sure the auth token cookie is not set
    assert "auth_token" not in response.cookies

    result = response.data["result"]

    assert result["mfa_required"] == True


def test_logout(get_api_client, get_user):
    """
    Ensure the account is logged out
    """
    user, client, response = get_login_response(get_user, get_api_client)

    url = reverse("auth-logout")
    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.cookies["auth_token"].value == ""
