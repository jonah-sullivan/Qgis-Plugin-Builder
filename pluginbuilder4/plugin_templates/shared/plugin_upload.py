#!/usr/bin/env python
"""This script uploads a plugin package to the plugin repository.
Authors: A. Pasotti, V. Picavet
git sha              : $TemplateVCSFormat
"""

import base64
import getpass
import http.client
import os
import sys
import urllib.parse
import urllib.request
import uuid
import zipfile
from optparse import OptionParser

import defusedxml.ElementTree as ET  # noqa: N817

# Configuration
PROTOCOL = "https"
SERVER = "plugins.qgis.org"
PORT = "443"
ENDPOINT = "/plugins/RPC2/"
REST_UPLOAD_URL = (
    "https://plugins.qgis.org/plugins/api/{package_name}/version/add/"
)


def _get_package_name_from_zip(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return zf.namelist()[0].split("/")[0]


def _post_upload_token(zip_path, token):
    """Upload plugin via the REST API using a JWT token."""
    package_name = _get_package_name_from_zip(zip_path)
    url = REST_UPLOAD_URL.format(package_name=package_name)
    boundary = uuid.uuid4().hex
    filename = os.path.basename(zip_path)
    with open(zip_path, "rb") as f:
        file_data = f.read()
    body = (
        (
            "--%s\r\n"
            'Content-Disposition: form-data; name="package"; filename="%s"\r\n'
            "Content-Type: application/zip\r\n\r\n" % (boundary, filename)
        ).encode()
        + file_data
        + ("\r\n--%s--\r\n" % boundary).encode()
    )
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must use http or https scheme: %s" % url)
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": "Bearer %s" % token,
            "Content-Type": "multipart/form-data; boundary=%s" % boundary,
            "User-Agent": "python-requests/2.32.3",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:  # nosec B310
        return resp.status, resp.read()


def _post_upload(address, plugin_data):
    """POST a plugin.upload XML-RPC call and return the raw response bytes."""
    parsed = urllib.parse.urlparse(address)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Address must use http or https scheme: %s" % address)

    encoded = base64.b64encode(plugin_data).decode("ascii")
    payload = (
        (
            "<?xml version='1.0'?>"
            "<methodCall>"
            "<methodName>plugin.upload</methodName>"
            "<params><param>"
            "<value><base64>{}</base64></value>"
            "</param></params>"
            "</methodCall>"
        )
        .format(encoded)
        .encode("utf-8")
    )

    auth = base64.b64encode(
        "{}:{}".format(parsed.username, parsed.password).encode()
    ).decode("ascii")
    headers = {"Content-Type": "text/xml", "Authorization": "Basic " + auth}
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    if parsed.scheme == "https":
        conn = http.client.HTTPSConnection(parsed.hostname, port)
    else:
        conn = http.client.HTTPConnection(parsed.hostname, port)

    conn.request("POST", parsed.path, body=payload, headers=headers)
    return conn.getresponse().read()


def _parse_response(xml_data):
    """Parse an XML-RPC response using defusedxml; raise on fault."""
    root = ET.fromstring(xml_data)
    fault = root.find("fault")
    if fault is not None:
        members = {}
        for member in fault.iter("member"):
            name = member.find("name").text
            value_el = member.find("value")
            members[name] = next(iter(value_el), value_el).text
        raise RuntimeError("Fault {faultCode}: {faultString}".format(**members))
    return tuple(int(v.text) for v in root.iter("int"))


def main(parameters, arguments):
    if parameters.token:
        print("Uploading using token authentication...")
        try:
            status, body = _post_upload_token(arguments[0], parameters.token)
            print("HTTP %s: %s" % (status, body.decode()))
        except urllib.error.HTTPError as err:
            print("HTTP error %s: %s" % (err.code, err.read().decode()))
            sys.exit(1)
        except urllib.error.URLError as err:
            print("Connection error: %s" % err.reason)
            sys.exit(1)
        return

    address = ("{protocol}://{username}:{password}@{server}:{port}{endpoint}").format(
        protocol=PROTOCOL,
        username=parameters.username,
        password=parameters.password,
        server=parameters.server,
        port=parameters.port,
        endpoint=ENDPOINT,
    )
    print("Connecting to: %s" % hide_password(address))

    try:
        with open(arguments[0], "rb") as handle:
            response_data = _post_upload(address, handle.read())
        plugin_id, version_id = _parse_response(response_data)
        print("Plugin ID: %s" % plugin_id)
        print("Version ID: %s" % version_id)
    except http.client.HTTPException as err:
        print("A protocol error occurred")
        print("Error: %s" % err)
    except RuntimeError as err:
        print("A fault occurred")
        print(str(err))


def hide_password(url, start=6):
    """Returns the http url with password part replaced with '*'."""
    start_position = url.find(":", start) + 1
    end_position = url.find("@")
    return "%s%s%s" % (
        url[:start_position],
        "*" * (end_position - start_position),
        url[end_position:],
    )


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [options] plugin.zip")
    parser.add_option(
        "-t",
        "--token",
        dest="token",
        help="JWT token for plugin site. "
        "You can use environment variable 'PLUGIN_UPLOAD_TOKEN'. "
        "When provided, the token REST API is used instead of XML-RPC.",
        metavar="TOKEN",
    )
    parser.add_option(
        "-w",
        "--password",
        dest="password",
        help="Password for plugin site. "
        "You can use environment variable 'PLUGIN_UPLOAD_PASSWORD', "
        "or the password will be prompted on runtime.",
        metavar="******",
    )
    parser.add_option(
        "-u",
        "--username",
        dest="username",
        help="Username of plugin site. "
        "You can use environment variable 'PLUGIN_UPLOAD_USERNAME', "
        "or the username will be prompted on runtime.",
        metavar="user",
    )
    parser.add_option(
        "-p", "--port", dest="port", help="Server port to connect to", metavar="80"
    )
    parser.add_option(
        "-s",
        "--server",
        dest="server",
        help="Specify server name",
        metavar="plugins.qgis.org",
    )
    options, args = parser.parse_args()
    if len(args) != 1:
        print("Please specify zip file.\n")
        parser.print_help()
        sys.exit(1)
    if not options.token:
        options.token = os.environ.get("PLUGIN_UPLOAD_TOKEN")
    if not options.token:
        # Fall through to username/password auth
        if not options.server:
            options.server = SERVER
        if not options.port:
            options.port = PORT
        if not options.username:
            username = os.environ.get("PLUGIN_UPLOAD_USERNAME")
            if username:
                options.username = username
            else:
                username = getpass.getuser()
                print("Please enter user name [%s] :" % username, end=" ")
                res = input()
                options.username = res if res != "" else username
        if not options.password:
            password = os.environ.get("PLUGIN_UPLOAD_PASSWORD")
            if password:
                options.password = password
            else:
                options.password = getpass.getpass()
    main(options, args)
