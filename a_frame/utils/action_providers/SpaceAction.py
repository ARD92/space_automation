import abc
from a_frame.utils.action_providers.action_base import ActionBase
from lxml import etree
import urllib2
import base64
import platform
import json
import ssl
from urllib2 import HTTPError

import argparse

class SpaceAction(ActionBase):
    """
        Simple SPACE action provider
        This is a "standalone" action, meaning it will be executed without an endpoint being passed in
    """

    # inherited set_global_options from action_base.py will overwrite all of these automatically from the
    # "create_template" selections
 	username = ""
	password = ""
	salt_master_ip = ""

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request
        :param template: the completed template from the user or API
        :return Boolean based on execution outcome.
        """
        # print "executing %s" % template



        # ensure no CRLF has snuck through
        template = template.replace('\r\n', '\n')

        data = template + "\n\n"
        print "Request type: %s" % self.request_type

        if self.request_type == "publish_event":
            try:
                
                json_in_string =  self.format_results(template)
		print 'Parsing Args from JEAP'
		parser = argparse.ArgumentParser(description='saltstack event system')

		parser.add_argument('device_ip', type=str, help='IP of Juniper Device')
		print 'firing event to salt master!'

		caller=salt.client.Caller()
		caller.sminion.functions['event.send'](
		'myco/myevent/success',
		{
		'message': json_in_string
		})

		print 'DONE SENDING TO SALT MASTER'


            except Exception as ex:
                print str(ex)
                return "Error! %s" % str(ex)
        else:
            # this is a subscribe_to_event attempt
            try:
                print('subscribe_to_event yet to be implemented')
            except Exception as ex:
		print('exception for subscribe')
    @staticmethod
    def format_results(results):
        """
        detects string format (xml || json) and formats appropriately
        :param results: string from urlopen
        :return: formatted string output
        """
        # is the result valid json?
        try:
            json_string = json.loads(results)
            print "Found JSON results"
            return json.dumps(json_string, indent=4)
        except ValueError:
            # this isn't xml or json, so just return it!
            print "Unknown results!"
            return results

    def connect_to_keystone(self):
        """
        connects to Keystone in the specified project scope
        :return: boolean if successful
        """

        _auth_json = """
            { "auth": {
                "identity": {
                  "methods": ["password"],
                  "password": {
                    "user": {
                      "name": "%s",
                      "domain": { "id": "default" },
                      "password": "%s"
                    }
                  }
                },
                  "scope": {
                        "project": {
                            "domain": {
                                "id": "default"
                            },
                            "name": "%s"
                        }
                    }
                }
            }
            """ % (self.username, self.password, self.keystone_project)

      
        return True
