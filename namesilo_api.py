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

import os
import xml.etree.ElementTree as ETree
from time import strftime

NAMESILO_COM_API = "https://www.namesilo.com/api"
NAMESILO_API_IMPLEMENTED_OPERATIONS = {"dnsListRecords", "dnsUpdateRecord"}

class NameSiloAPI:
	def __init__(self, key, web_worker, domain, hosts=None):
		print("NameSilo connection called for {} at {}.".format(domain, strftime("%x %H:%M:%S")))
		self.domain = domain
		self._namesilo_api_params = {
			"version": "1",
			"type": "xml",
			"key": key,
			"domain": self.domain
		}
		self._web_worker = web_worker
		self.hosts = hosts
		self.current_records = []
		self.retrieve_resource_records()  # populate.

	def _api_connection(self, operation, **html_params) -> ETree.ElementTree:
		if operation in NAMESILO_API_IMPLEMENTED_OPERATIONS:
			_api_call = {**html_params, **self._namesilo_api_params}
			_api_url = str.join("/", [NAMESILO_COM_API, operation])
			# print("API connection:", __api_url, __api_call)
			_ret = self._web_worker.get(_api_url, params=_api_call)
			_ret.raise_for_status()
			_ret = ETree.XML(_ret.text)
			try:
				success = _ret.find(".//reply/code").text
			except AttributeError:
				raise ValueError("Could not parse API response.")
			if success != "300":
				raise ValueError("API Operation failed with code {}.".format(success))
			return _ret
		else:
			raise NotImplementedError("Invalid operation: {} is currently unsupported or undefined.".format(operation))

	def retrieve_resource_records(self):
		print("Retrieving records for {}".format(self.domain))
		current_records = self._api_connection("dnsListRecords")
		for current_resource_record in current_records.iter("resource_record"):
			self.current_records.append(
				dict(
					(resource_record.tag, resource_record.text)
					for resource_record
					in current_resource_record.iter()
				)
			)
		print("{} records retrieved for {}".format(len(self.current_records), self.domain))

	def dynamic_dns_update(self, ip):
		print("DDNS update starting for domain: {}".format(self.domain))
		hosts_requiring_updates = (
			record for record
			in self.current_records
			if record["host"] in self.hosts.keys()
			   and (
				   record["type"] == "A"
				   and record["value"] != ip
			   )
		)
		_count = 0
		_failed = 0
		for host in hosts_requiring_updates:
			print("DDNS update required for {}".format(host["host"]))
			__api_params = {
				"rrid": host["record_id"],
				"rrhost": self.hosts[host["host"]],
				"rrvalue": ip
			}
			try:
				self._api_connection("dnsUpdateRecord", **__api_params)
			except ValueError:
				print("DDNS failed to update {}".format(host["host"]))
				_failed += 1
				pass
			except NotImplementedError:
				print("DDNS failed to update {}".format(host["host"]))
				_failed += 1
				pass
			_count += 1
			print("DDNS successfully updated {}".format(host["host"]))
		print("DDNS update complete for {}.  {} hosts required updates. {} errors.".format(self.domain, _count, _failed))
