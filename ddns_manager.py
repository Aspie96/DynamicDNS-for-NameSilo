'''
Copyright (c) 2017 BENJAMIN RONSER
Copyright (c) 2018 VALENTINO GIUDICE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from namesilo_api import NameSiloAPI
import requests
from time import strftime

domain = "example.com"
hosts = ["", "www", "dom1", "dom2"]

NAMESILO_API_KEY = "SECRET"

_web_worker = requests.session()

api = NameSiloAPI(NAMESILO_API_KEY, _web_worker, domain, hosts)

def get_my_ip():
	_web_worker.get("https://api.ipify.org/?format=json").json()["ip"]

current_ip = get_my_ip()

def update_records(ip):
	print("DDNS operation started at {}".format(strftime("%x %H:%M:%S")))
	api.dynamic_dns_update(ip)

update_records(current_ip)
