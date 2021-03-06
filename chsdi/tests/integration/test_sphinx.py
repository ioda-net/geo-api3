# -*- coding: utf-8  -*-

import unittest
from chsdi.lib.sphinxapi import sphinxapi
from tasks.config import load_config


class Test_SphinxApi(unittest.TestCase):
    def setUp(self):
        self.search_config = load_config()['search']

    def _callFUT(self):
        api = sphinxapi.SphinxClient()
        return api

    def test_sphinx_api(self):
        api = self._callFUT()
        docs = [
            'this is my test text to be highlighted',
            'this is another test text to be highlighted'
        ]
        words = 'test text'
        index = 'test1'
        opts = {
            'before_match': '<b>',
            'after_match': '</b>',
            'chunk_separator': ' ... ',
            'limit': 400,
            'around': 15
        }
        res = api.BuildExcerpts(docs, index, words, opts)
        self.assertFalse(res)

    def test_sphinx_api_query(self):
        import sys

        api = self._callFUT()
        q = ''
        mode = sphinxapi.SPH_MATCH_ALL
        host = self.search_config['host']
        port = self.search_config['port']
        index = '*'
        filtercol = 'group_id'
        filtervals = []
        sortby = ''
        limit = 0
        i = 1
        while (i < len(sys.argv)):
            arg = sys.argv[i]
            if arg == '-h' or arg == '--host':
                i += 1
                host = sys.argv[i]
            elif arg == '-p' or arg == '--port':
                i += 1
                port = int(sys.argv[i])
            elif arg == '-i':
                i += 1
                index = sys.argv[i]
            elif arg == '-s':
                i += 1
                sortby = sys.argv[i]
            elif arg == '-a' or arg == '--any':
                mode = sphinxapi.SPH_MATCH_ANY
            elif arg == '-b' or arg == '--boolean':
                mode = sphinxapi.SPH_MATCH_BOOLEAN
            elif arg == '-e' or arg == '--extended':
                mode = sphinxapi.SPH_MATCH_EXTENDED
            elif arg == '-f' or arg == '--filter':
                i += 1
                filtercol = sys.argv[i]
            elif arg == '-v' or arg == '--value':
                i += 1
                filtervals.append(int(sys.argv[i]))
            elif arg == '-l' or arg == '--limit':
                i += 1
                limit = int(sys.argv[i])
            else:
                q = '%s%s ' % (q, arg)
            i += 1

        api.SetServer(host, port)
        api.SetMatchMode(mode)
        if filtervals:
            api.SetFilter(filtercol, filtervals)
        if sortby:
            api.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, sortby)
        if limit:
            api.SetLimits(0, limit, max(limit, 1000))
        res = api.Query(q, index)
        self.assertTrue(isinstance(res, dict))
