# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import urllib
import json

from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):

    TRANSFERS_FILES = True

    PARAM_DEFAULTS = dict(
        base_url = 'http://localhost:5000',
        request_method = 'GET',
        login_cookie   = None,
        login_user     = None,
        login_password = None,
        cgi_path = '/webapi/',
        cgi_name = 'entry.cgi',
        api_name    = None,
        api_version = '1',
        api_method  = None,
        api_params  = None,
        request_json = None,
    )

    def extract_params(self):
        """return the params with none items removed
        :return: a dictionary of the params, no Nones, and correctly prioritized to the user input
        """

        # Capture the default params
        task_args = self.PARAM_DEFAULTS.copy()

        # Undo the json -> python-literal auto-transformation made by jinja2
        # follow https://github.com/ansible/ansible/issues/68643#issue-592816310
        if ("api_params") in self._task.args:
            if ("compound") in self._task.args["api_params"]:
                compound = self._task.args["api_params"]["compound"]
                if (isinstance(compound, dict) or type(compound) == list):
                    json_str = json.dumps(compound)
                    self._task.args["api_params"]["compound"] = json_str
                else:
                    # mostly an AnsibleUnicode type
                    # and jinja template didn't touch it
                    pass

        # Overwrite the params with the input args
        task_args.update(self._task.args)
        # Remove the none items
        for arg in task_args.keys():
            if task_args[arg] is not None:
                print("{}:\t {}".format(arg, type(task_args[arg])))
        return {k: v for k, v in task_args.items() if v is not None}

    def build_uri(task_args):
        """ Create base_url/cgi_path/cgi_name and set the GET or POST method

        :param dict task_args: the arguments of the request, including the url, path, method, ... etc.
        :return: A uri representing the request, ie: http://localhost:5000/webapi/entry.cgi
                 It will include the username and password, at least for the first time
                 before having the login_cookie
        """
        uri_params = dict(
            url = "%s/%s/%s" % (task_args['base_url'], task_args['cgi_path'].strip('/'), task_args['cgi_name']),
            method = task_args['request_method'],
        )

        if 'login_cookie' in task_args:
            uri_params['headers'] = dict(Cookie = task_args['login_cookie'])

        if task_args['request_method'] == 'POST':
            if 'request_json' in task_args:
                # fill json body
                uri_params['body'] = task_args['request_json']
                uri_params['body_format'] = 'json'
            else:
                # fill form-urlencoded body
                tmp_body = dict(
                    api     = task_args['api_name'],
                    version = task_args['api_version'],
                    method  = task_args['api_method'],
                )

                if 'api_params' in task_args:
                    tmp_body.update(task_args['api_params'])

                uri_params['body'] = tmp_body
                uri_params['body_format'] = 'form-urlencoded'

        elif task_args['request_method'] == 'GET':
            uri_params['url'] += '?api=%s&version=%s&method=%s' %(
                                  task_args['api_name'],
                                  task_args['api_version'],
                                  task_args['api_method']
                                  )

            # encode further API params into the URL
            # ie: include the username and password for the login
            if 'api_params' in task_args:
                try:
                    uri_params['url'] += '&%s' % urllib.parse.urlencode(task_args['api_params'])
                except AttributeError:
                    uri_params['url'] += '&%s' % urllib.urlencode(task_args['api_params'])

        return uri_params

    def is_request_failing(result):
        return (result.get('failed', False) or
                result.get('json', {}).get('success', None) == False or
                result.get('json', {}).get('data', {}).get('has_fail', None) == True
               )

    def run(self, tmp=None, task_vars=None):
        self._supports_async = True

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        # Build task args
        task_args = self.extract_params()

        # Build URI compliant with synology API
        uri_params = ActionModule.build_uri(task_args)

        result = self._execute_module('uri',
                                      module_args=uri_params,
                                      task_vars=task_vars,
                                      wrap_async=self._task.async_val)

        if not self._task.async_val:
            self._remove_tmp_path(self._connection._shell.tmpdir)

        if ActionModule.is_request_failing(result):
            result['failed'] = True

        return result
