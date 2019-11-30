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
        login_cookie = None,
        login_user = None,
        login_password = None,
        cgi_path = '/webapi/',
        cgi_name = 'entry.cgi',
        api_name = None,
        api_version = '1',
        api_method = None,
        api_params = None,
        request_json = None,
    )

    def run(self, tmp=None, task_vars=None):
        self._supports_async = True

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        # Build task args
        task_args = self.PARAM_DEFAULTS.copy()
        task_args.update(self._task.args)
        for arg in task_args.keys():
            if task_args[arg] is None:
                del task_args[arg]

        # Build 'uri' module params
        uri_params = dict(
            url = "%s/%s/%s" % (task_args['base_url'], task_args['cgi_path'].strip('/'), task_args['cgi_name']),
            method = task_args['request_method'],
        )
        if 'login_cookie' in task_args:
            uri_params['headers'] = dict(Cookie = task_args['login_cookie'])
        if task_args['request_method'] == 'POST':
            if 'request_json' in task_args:
                uri_params['body'] = task_args['request_json']
                uri_params['body_format'] = 'json'
            else:
                tmp_body = dict(
                    api = task_args['api_name'],
                    version = task_args['api_version'],
                    method = task_args['api_method'],
                )
                if 'api_params' in task_args:
                    tmp_body.update(task_args['api_params'])
                uri_params['body'] = tmp_body
                uri_params['body_format'] = 'form-urlencoded'
        elif task_args['request_method'] == 'GET':
            uri_params['url'] += '?api=%s&version=%s&method=%s' % (task_args['api_name'], task_args['api_version'], task_args['api_method'])
            if 'api_params' in task_args:
                try:
                    uri_params['url'] += '&%s' % urllib.parse.urlencode(task_args['api_params'])
                except AttributeError:
                    uri_params['url'] += '&%s' % urllib.urlencode(task_args['api_params'])

        result = self._execute_module('uri', module_args=uri_params, task_vars=task_vars, wrap_async=self._task.async_val)

        if not self._task.async_val:
            self._remove_tmp_path(self._connection._shell.tmpdir)

        if result.get('failed', False) or (result.get('json', {}).get('success', None) == False):
            result['failed'] = True

        return result
