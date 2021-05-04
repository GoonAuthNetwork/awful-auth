from datetime import datetime
from logging import Logger
from typing import Optional
from bs4 import BeautifulSoup
import httpx

from app.config import sa_settings
from app.models.goon_auth import GoonAuthStatus

__cookies = sa_settings.create_cookie_container()


async def check_auth_status(user_name: str, hash: str) -> Optional[GoonAuthStatus]:
    profile = await get_profile(user_name)
    if profile.status_code != 200 or hash not in profile.text:
        return None

    # Here be scraping dragons
    soup = BeautifulSoup(profile.text, "html.parser")

    # Pull out as much as we can from the profile
    try:
        user_id = int(soup.select_one("input[name=userid]").get("value"))
        reg_date_str = soup.select_one("dd.registered").get_text()
        reg_date = datetime.strptime(reg_date_str, "%b %d, %Y")

    except (AttributeError, ValueError):
        Logger.error(f"Failed to parse SA Profile for user: `{user_name}`")
        return None

    # Then move on to the rap sheet to check ban status
    # TODO: Add all of this, maybe
    """
    rap_sheet = await get_rap_sheet(user_id)
    if profile.status_code != 200:
        return None

    soup = BeautifulSoup(rap_sheet.text, "html.parser")
    """

    return GoonAuthStatus(
        validated=True,
        user_name=user_name,
        user_id=int(user_id),
        register_date=reg_date,
        # TODO: add permabanned checks, query banlist.php?username=
        # permabanned=Something
    )


async def get_profile(user_name: str) -> httpx.Response:
    async with httpx.AsyncClient(cookies=__cookies) as client:
        url = sa_settings.create_profile_url(user_name)
        return await client.get(url)


async def get_rap_sheet(user_id: str) -> httpx.Response:
    async with httpx.AsyncClient(cookies=__cookies) as client:
        url = sa_settings.create_rap_sheet_url(user_id)
        return await client.get(url)
