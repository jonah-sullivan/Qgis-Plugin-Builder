#!/usr/bin/env python
"""This script uploads a plugin package to the plugin repository.
Authors: A. Pasotti, V. Picavet
git sha              : $TemplateVCSFormat
"""

import base64
import http.client
import os
import sys
import getpass
import urllib.parse
from optparse import OptionParser

import defusedxml.ElementTree as ET

# Configuration
PROTOCOL = "https"
SERVER = "plugins.qgis.org"
PORT = "443"
ENDPOINT = "/plugins/RPC2/"


def _post_upload(address, plugin_data):
    """POST a plugin.upload XML-RPC call and return the raw response bytes."""
    parsed = urllib.parse.urlparse(address)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Address must use http or https scheme: %s" % address)

    encoded = base64.b64encode(plugin_data).decode("ascii")
    payload = (
        "<?xml version='1.0'?>"
        "<methodCall>"
        "<methodName>plugin.upload</methodName>"
        "<params><param>"
        "<value><base64>{}</base64></value>"
        "</param></params>"
        "</methodCall>"
    ).format(encoded).encode("utf-8")

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
        raise RuntimeError(
            "Fault {faultCode}: {faultString}".format(**members)
        )
    return tuple(int(v.text) for v in root.iter("int"))


def main(parameters, arguments):
    address = (
        "{protocol}://{username}:{password}@{server}:{port}{endpoint}"
    ).format(
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
        "-p", "--port", dest="port",
        help="Server port to connect to", metavar="80"
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
