import re, math, logging, secrets, mimetypes, time
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from plugins.start import decode, encode 
from datetime import datetime
from plugins.database import record_visit, get_count
from TechVJ.bot import multi_clients, work_loads, TechVJBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page
from TechVJ.util.file_properties import get_file_ids

routes = web.RouteTableDef()

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#08080e">
    <title>CodeX OTT — Stream Server</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body {
            background: #08080e;
            color: #e8e8f0;
            font-family: 'Rajdhani', sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            gap: 20px;
        }
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse 80% 60% at 50% 50%, rgba(229,9,20,0.1), transparent 70%);
            pointer-events: none;
        }
        .logo {
            font-family: 'Bebas Neue', cursive;
            font-size: 48px;
            letter-spacing: 10px;
            color: #fff;
            text-shadow: 0 0 40px rgba(229,9,20,0.5);
            position: relative;
            z-index: 1;
        }
        .logo span { color: #e50914; }
        .line {
            width: 100px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #e50914, #f5c518, transparent);
            position: relative;
            z-index: 1;
        }
        .status {
            font-size: 13px;
            letter-spacing: 4px;
            color: #7777aa;
            position: relative;
            z-index: 1;
        }
        .status span {
            color: #22c55e;
            font-weight: 700;
        }
        .powered {
            position: fixed;
            bottom: 20px;
            font-size: 10px;
            letter-spacing: 3px;
            color: rgba(255,255,255,0.15);
        }
        .powered span { color: rgba(229,9,20,0.4); }
    </style>
</head>
<body>
    <div class="logo"><span>CODE</span>X OTT</div>
    <div class="line"></div>
    <div class="status">STREAM SERVER <span>ONLINE</span></div>
    <div class="powered">POWERED BY <span>CODEXMOMO</span></div>
</body>
</html>
"""

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text=html_content, content_type='text/html')

@routes.get(r"/{path}/{user_path}/{second}/{third}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        user_path = request.match_info["user_path"]
        sec = request.match_info["second"]
        th = request.match_info["third"]
        id = int(await decode(path))
        user_id = int(await decode(user_path))
        secid = int(await decode(sec))
        thid = int(await decode(th))
        return web.Response(text=await render_page(id, user_id, secid, thid), content_type='text/html')
    except Exception as e:
        logging.error(f"STREAM ERROR: {str(e)}")
        return web.Response(text=html_content, content_type='text/html')
    return 

@routes.post('/click-counter')
async def handle_click(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        today = datetime.now().strftime('%Y-%m-%d')

        user_agent = request.headers.get('User-Agent')
        is_chrome = "Chrome" in user_agent or "Google Inc" in user_agent

        if is_chrome:
            visited_cookie = request.cookies.get('visited')
        else:
            return

        if visited_cookie == today:
            return
        else:
            response = web.Response(text="Hello, World!")
            response.set_cookie('visited', today, max_age=24*60*60)
            u = get_count(user_id)
            if u:
                c = int(u + 1)
                record_visit(user_id, c)
            else:
                c = int(1)
                record_visit(user_id, c)
            return response
    except:
        pass

@routes.get('/{short_link}', allow_head=True)
async def get_original(request: web.Request):
    short_link = request.match_info["short_link"]
    link = f"{STREAM_URL}link?{short_link}"
    raise web.HTTPFound(link)

@routes.get('/link', allow_head=True)
async def visits(request: web.Request):
    # Get the full query string after /link?
    query_string = request.query_string  # e.g. dT04NDM1MjIx...
    # Try direct params first (u, w, s, t)
    user = request.query.get('u')
    watch = request.query.get('w')
    second = request.query.get('s')
    third = request.query.get('t')
    
    if user and watch:
        # Already decoded params
        data = await encode(watch)
        user_id = await encode(user)
        sec_id = await encode(second) if second else await encode('0')
        th_id = await encode(third) if third else await encode('0')
        link = f"{STREAM_URL}{data}/{user_id}/{sec_id}/{th_id}"
        raise web.HTTPFound(link)
    else:
        # query_string is the encoded payload - decode it first
        original = await decode(query_string)
        if original:
            from urllib.parse import parse_qs
            params = dict(p.split('=') for p in original.split('&') if '=' in p)
            user = params.get('u', '0')
            watch = params.get('w', '0')
            second = params.get('s', '0')
            third = params.get('t', '0')
            data = await encode(watch)
            user_id = await encode(user)
            sec_id = await encode(second)
            th_id = await encode(third)
            link = f"{STREAM_URL}{data}/{user_id}/{sec_id}/{th_id}"
            raise web.HTTPFound(link)
        else:
            return web.Response(text=html_content, content_type='text/html')

@routes.get(r"/dl/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
