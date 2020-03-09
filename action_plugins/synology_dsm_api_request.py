# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import urllib

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
        """return the params with none items removed"""
        task_args = self.PARAM_DEFAULTS.copy()
        # overwrite with the input args
        task_args.update(self._task.args)
        return {k: v for k, v in task_args.items() if v is not None}

    def build_uri(task_args):
        # create base_url/cgi_path/cgi_name and set the GET or POST method
        # ie: http://localhost:5000/webapi/entry.cgi
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
        return result.get('failed', False) or (result.get('json', {}).get('success', None) == False)

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
