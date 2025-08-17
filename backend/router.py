from typing import Annotated
from fastapi import APIRouter, Body, Query
from fastapi.responses import RedirectResponse
import urllib.parse

import aiohttp
import jwt

from state_storage import state_storage
from oauth_google import generate_google_oauth_redirect_uri
from config import settings

router = APIRouter(prefix="/auth")


@router.get("/google/url")
def get_google_oauth_redirect_uri():
    uri = generate_google_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=302)


@router.get("/google/callback")
async def handle_code(
    code: str,
    state: str,
):
    if state not in state_storage:
        raise
    else:
        print("Стейт корректный")
    google_token_url = "https://oauth2.googleapis.com/token"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=google_token_url,
            data={
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:8000/auth/google/callback",
                "code": code,
            },
            ssl=False,
        ) as response:
            res = await response.json()
            print(f"{res=}")
            id_token = res["id_token"]
            access_token = res["access_token"]
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://www.googleapis.com/drive/v3/files",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            ssl=False,
        ) as response:
            res = await response.json()
            print(f"{res=}")
            files = [item["name"] for item in res["files"]]

    redirect_url = "http://localhost:3000/auth/google"
    params = {
        "userName": user_data.get("name"),
        "picUrl": user_data.get("picture"),
        "fileNames": ",".join(files)
    }
    encoded_params = urllib.parse.urlencode(params)

    return RedirectResponse(f"{redirect_url}?{encoded_params}")