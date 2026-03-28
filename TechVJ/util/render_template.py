import re
import jinja2
import logging
import aiohttp
from info import *
import urllib.parse
from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.human_readable import humanbytes
from TechVJ.server.exceptions import InvalidHash
from pyrogram.errors import FloodWait
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size, get_file_ids
from plugins.database import db

async def render_page(id, user, secid, thid, src=None):
    file_data_one = None
    file_data_two = None
    file_data_three = None
    if id != 0:
        try:
            fileone = await TechVJBot.get_messages(int(LOG_CHANNEL), int(id))
        except:
            fileone = await TechVJBackUpBot.get_messages(int(LOG_CHANNEL), int(id))
        file_data_one = await get_file_ids(fileone)

        src = urllib.parse.urljoin(
            STREAM_URL + "dl/",
            f"{id}/{urllib.parse.quote_plus(str(file_data_one.file_name))}?hash={file_data_one.unique_id[:6]}",
        )
        quality = "480"
    else:
        src = None
        quality = None

    if secid != 0:
        try:
            filetwo = await TechVJBot.get_messages(int(LOG_CHANNEL), int(secid))
        except:
            filetwo = await TechVJBackUpBot.get_messages(int(LOG_CHANNEL), int(secid))
        file_data_two = await get_file_ids(filetwo)
        file_url_two = urllib.parse.urljoin(
            STREAM_URL + "dl/",
            f"{secid}/{urllib.parse.quote_plus(str(file_data_two.file_name))}?hash={file_data_two.unique_id[:6]}",
        )
        quality_two = "720"
    else:
        file_url_two = None
        quality_two = None

    if thid != 0:
        try:
            filethree = await TechVJBot.get_messages(int(LOG_CHANNEL), int(thid))
        except:
            filethree = await TechVJBackUpBot.get_messages(int(LOG_CHANNEL), int(thid))
        file_data_three = await get_file_ids(filethree)
        file_url_three = urllib.parse.urljoin(
            STREAM_URL + "dl/",
            f"{thid}/{urllib.parse.quote_plus(str(file_data_three.file_name))}?hash={file_data_three.unique_id[:6]}",
        )
        quality_three = "1080"
    else:
        file_url_three = None
        quality_three = None

    if file_data_one == None:
        if file_data_two == None:
            file_data = file_data_three
        else:
            file_data = file_data_two
    else:
        file_data = file_data_one

    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)
    if tag in ["document", "video", "audio"]:
        template_file = "TechVJ/template/req.html"
    else:
        template_file = "TechVJ/template/dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get("Content-Length")))

    with open(template_file) as f:
        template = jinja2.Template(f.read())

    old_file_name = file_data.file_name.replace("_", " ")
    file_name_clean = clean_file_name(old_file_name)
    file_name = remove_after_year(file_name_clean)
    link = await db.get_link(int(user))
    name = await db.get_name(int(user))
    return template.render(
        file_name=file_name,
        file_url=src,
        file_url_two=file_url_two,
        file_url_three=file_url_three,
        file_size=file_size,
        user_id=user,
        link=link,
        name=name
    )


def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name)) 
    unwanted_chars = ['[', ']', '(', ')', '{', '}']

    for char in unwanted_chars:
        file_name = file_name.replace(char, '')

    return ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.') and not x.startswith('t.me'), file_name.split()))

def remove_after_year(filename):
    match = re.search(r'\d{4}', filename)
    if match:
        year_index = match.start()
        year_end_index = match.end()
        new_filename = filename[:year_end_index].strip()
        return new_filename 