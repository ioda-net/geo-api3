#
# $Id: sphinxapi.py 3436 2012-10-08 09:17:18Z kevg $
#
# Python version of Sphinx searchd client (Python API)
#
# Copyright (c) 2006, Mike Osadnik
# Copyright (c) 2006-2012, Andrew Aksyonoff
# Copyright (c) 2008-2012, Sphinx Technologies Inc
# All rights reserved
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License. You should have
# received a copy of the GPL license along with this program; if you
# did not, you can find it at http://www.gnu.org/
#

import select
import socket
import struct


# known searchd commands
SEARCHD_COMMAND_SEARCH = 0
SEARCHD_COMMAND_EXCERPT = 1
SEARCHD_COMMAND_UPDATE = 2
SEARCHD_COMMAND_KEYWORDS = 3
SEARCHD_COMMAND_PERSIST = 4
SEARCHD_COMMAND_STATUS = 5
SEARCHD_COMMAND_FLUSHATTRS = 7

# current client-side command implementation versions
VER_COMMAND_SEARCH = 0x119
VER_COMMAND_EXCERPT = 0x104
VER_COMMAND_UPDATE = 0x102
VER_COMMAND_KEYWORDS = 0x100
VER_COMMAND_STATUS = 0x100
VER_COMMAND_FLUSHATTRS = 0x100

# known searchd status codes
SEARCHD_OK = 0
SEARCHD_ERROR = 1
SEARCHD_RETRY = 2
SEARCHD_WARNING = 3

# known match modes
SPH_MATCH_ALL = 0
SPH_MATCH_ANY = 1
SPH_MATCH_PHRASE = 2
SPH_MATCH_BOOLEAN = 3
SPH_MATCH_EXTENDED = 4
SPH_MATCH_FULLSCAN = 5
SPH_MATCH_EXTENDED2 = 6

# known ranking modes (extended2 mode only)
SPH_RANK_PROXIMITY_BM25 = 0  # default mode, phrase proximity major factor and BM25 minor one
SPH_RANK_BM25 = 1  # statistical mode, BM25 ranking only (faster but worse quality)
SPH_RANK_NONE = 2  # no ranking, all matches get a weight of 1
# simple word-count weighting, rank is a weighted sum of per-field keyword occurence counts
SPH_RANK_WORDCOUNT = 3
SPH_RANK_PROXIMITY = 4
SPH_RANK_MATCHANY = 5
SPH_RANK_FIELDMASK = 6
SPH_RANK_SPH04 = 7
SPH_RANK_EXPR = 8
SPH_RANK_TOTAL = 9

# known sort modes
SPH_SORT_RELEVANCE = 0
SPH_SORT_ATTR_DESC = 1
SPH_SORT_ATTR_ASC = 2
SPH_SORT_TIME_SEGMENTS = 3
SPH_SORT_EXTENDED = 4
SPH_SORT_EXPR = 5

# known filter types
SPH_FILTER_VALUES = 0
SPH_FILTER_RANGE = 1
SPH_FILTER_FLOATRANGE = 2

# known attribute types
SPH_ATTR_NONE = 0
SPH_ATTR_INTEGER = 1
SPH_ATTR_TIMESTAMP = 2
SPH_ATTR_ORDINAL = 3
SPH_ATTR_BOOL = 4
SPH_ATTR_FLOAT = 5
SPH_ATTR_BIGINT = 6
SPH_ATTR_STRING = 7
SPH_ATTR_MULTI = 0X40000001
SPH_ATTR_MULTI64 = 0X40000002

SPH_ATTR_TYPES = (SPH_ATTR_NONE,
                  SPH_ATTR_INTEGER,
                  SPH_ATTR_TIMESTAMP,
                  SPH_ATTR_ORDINAL,
                  SPH_ATTR_BOOL,
                  SPH_ATTR_FLOAT,
                  SPH_ATTR_BIGINT,
                  SPH_ATTR_STRING,
                  SPH_ATTR_MULTI,
                  SPH_ATTR_MULTI64)

# known grouping functions
SPH_GROUPBY_DAY = 0
SPH_GROUPBY_WEEK = 1
SPH_GROUPBY_MONTH = 2
SPH_GROUPBY_YEAR = 3
SPH_GROUPBY_ATTR = 4
SPH_GROUPBY_ATTRPAIR = 5


class SphinxClient:

    def __init__(self):
        """
        Create a new client object, and fill defaults.
        """
        self._host = 'localhost'                   # searchd host (default is "localhost")
        self._port = 9312                          # searchd port (default is 9312)
        self._path = None                          # searchd unix-domain socket path
        self._socket = None
        # how much records to seek from result-set start (default is 0)
        self._offset = 0
        # how much records to return from result-set starting at offset (default is 20)
        self._limit = 20
        self._mode = SPH_MATCH_ALL                 # query matching mode (default is SPH_MATCH_ALL)
        # per-field weights (default is 1 for all fields)
        self._weights = []
        # match sorting mode (default is SPH_SORT_RELEVANCE)
        self._sort = SPH_SORT_RELEVANCE
        self._sortby = ''                            # attribute to sort by (defualt is "")
        self._min_id = 0                             # min ID to match (default is 0)
        self._max_id = 0                             # max ID to match (default is UINT_MAX)
        self._filters = []                            # search filters
        self._groupby = ''                            # group-by attribute name
        # group-by function (to pre-process group-by attribute value with)
        self._groupfunc = SPH_GROUPBY_DAY
        # group-by sorting clause (to sort groups in result set with)
        self._groupsort = '@group desc'
        self._groupdistinct = ''                            # group-by count-distinct attribute
        self._maxmatches = 1000                          # max matches to retrieve
        self._cutoff = 0                             # cutoff to stop searching at
        self._retrycount = 0                             # distributed retry count
        self._retrydelay = 0                             # distributed retry delay
        self._anchor = {}                            # geographical anchor point
        self._indexweights = {}                            # per-index weights
        self._ranker = SPH_RANK_PROXIMITY_BM25       # ranking mode
        self._rankexpr = ''                            # ranking expression for SPH_RANK_EXPR
        # max query time, milliseconds (default is 0, do not limit)
        self._maxquerytime = 0
        self._timeout = 1.0                                     # connection timeout
        self._fieldweights = {}                            # per-field-name weights
        self._overrides = {}                            # per-query attribute values overrides
        # select-list (attributes or expressions, with optional aliases)
        self._select = '*'

        self._error = ''                            # last error message
        self._warning = ''                            # last warning message
        self._reqs = []                            # requests array for multi-query

    def __del__(self):
        if self._socket:
            self._socket.close()

    def SetServer(self, host, port=None):
        """
        Set searchd server host and port.
        """
        assert(isinstance(host, str))
        if host.startswith('/'):
            self._path = host
            return
        elif host.startswith('unix://'):
            self._path = host[7:]
            return
        self._host = host
        if isinstance(port, int):
            assert(port > 0 and port < 65536)
            self._port = port
        self._path = None

    def SetConnectTimeout(self, timeout):
        """
        Set connection timeout ( float second )
        """
        assert (isinstance(timeout, float))
        # set timeout to 0 make connaection non-blocking that is wrong so timeout
        # got clipped to reasonable minimum
        self._timeout = max(0.001, timeout)

    def _Connect(self):
        """
        INTERNAL METHOD, DO NOT CALL. Connects to searchd server.
        """
        if self._socket:
            # we have a socket, but is it still alive?
            sr, sw, _ = select.select([self._socket], [self._socket], [], 0)

            # this is how alive socket should look
            if len(sr) == 0 and len(sw) == 1:
                return self._socket

            # oops, looks like it was closed, lets reopen
            self._socket.close()
            self._socket = None

        try:
            if self._path:
                af = socket.AF_UNIX
                addr = self._path
                desc = self._path
            else:
                af = socket.AF_INET
                addr = (self._host, self._port)
                desc = '%s;%s' % addr
            sock = socket.socket(af, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect(addr)
        except socket.error as msg:
            if sock:
                sock.close()
            self._error = 'connection to %s failed (%s)' % (desc, msg)
            return

        v = struct.unpack('>L', sock.recv(4))[0]
        if v < 1:
            sock.close()
            self._error = 'expected searchd protocol version, got %s' % v
            return

        # all ok, send my version
        sock.send(struct.pack('>L', 1))
        return sock

    def _GetResponse(self, sock, client_ver):
        """
        INTERNAL METHOD, DO NOT CALL. Gets and checks response packet from searchd server.
        """
        (status, ver, length) = struct.unpack('>2HL', sock.recv(8))
        response = b''
        left = length
        while left > 0:
            chunk = sock.recv(left)
            if chunk:
                response += chunk
                left -= len(chunk)
            else:
                break

        if not self._socket:
            sock.close()

        # check response
        read = len(response)
        if not response or read != length:
            if length:
                self._error = \
                    'failed to read searchd response (status=%s, ver=%s, len=%s, read=%s)' \
                    % (status, ver, length, read)
            else:
                self._error = 'received zero-sized searchd response'
            return None

        # check status
        if status == SEARCHD_WARNING:
            wend = 4 + struct.unpack('>L', response[0:4])[0]
            self._warning = response[4:wend]
            return response[wend:]

        if status == SEARCHD_ERROR:
            self._error = b'searchd error: ' + response[4:]
            return None

        if status == SEARCHD_RETRY:
            self._error = b'temporary searchd error: ' + response[4:]
            return None

        if status != SEARCHD_OK:
            self._error = b'unknown status code %d' % status
            return None

        # check version
        if ver < client_ver:
            self._warning = \
                'searchd command v.%d.%d older than client\'s v.%d.%d, some options might not '\
                'work' % (ver >> 8, ver & 0xff, client_ver >> 8, client_ver & 0xff)

        return response

    def _Send(self, sock, req):
        """
        INTERNAL METHOD, DO NOT CALL. send request to searchd server.
        """
        total = 0
        while True:
            sent = sock.send(req[total:])
            if sent <= 0:
                break

            total = total + sent

        return total

    def SetLimits(self, offset, limit, maxmatches=0, cutoff=0):
        """
        Set offset and count into result set, and optionally set max-matches and cutoff limits.
        """
        assert (isinstance(offset, int) and 0 <= offset < 16777216)
        assert (isinstance(limit, int) and 0 < limit < 16777216)
        assert maxmatches >= 0
        self._offset = offset
        self._limit = limit
        if maxmatches > 0:
            self._maxmatches = maxmatches
        if cutoff >= 0:
            self._cutoff = cutoff

    def SetMaxQueryTime(self, maxquerytime):
        """
        Set maximum query time, in milliseconds, per-index. 0 means 'do not limit'.
        """
        assert(isinstance(maxquerytime, int) and maxquerytime > 0)
        self._maxquerytime = maxquerytime

    def SetMatchMode(self, mode):
        """
        Set matching mode.
        """
        assert(mode in [SPH_MATCH_ALL, SPH_MATCH_ANY, SPH_MATCH_PHRASE,
                        SPH_MATCH_BOOLEAN, SPH_MATCH_EXTENDED, SPH_MATCH_FULLSCAN,
                        SPH_MATCH_EXTENDED2])
        self._mode = mode

    def SetRankingMode(self, ranker, rankexpr=''):
        """
        Set ranking mode.
        """
        assert(ranker >= 0 and ranker < SPH_RANK_TOTAL)
        self._ranker = ranker
        self._rankexpr = rankexpr

    def SetSortMode(self, mode, clause=''):
        """
        Set sorting mode.
        """
        assert (mode in [SPH_SORT_RELEVANCE, SPH_SORT_ATTR_DESC, SPH_SORT_ATTR_ASC,
                         SPH_SORT_TIME_SEGMENTS, SPH_SORT_EXTENDED, SPH_SORT_EXPR])
        assert (isinstance(clause, str))
        self._sort = mode
        self._sortby = clause

    def SetFilter(self, attribute, values, exclude=0):
        """
        Set values set filter.
        Only match records where 'attribute' value is in given 'values' set.
        """
        assert(isinstance(attribute, str))
        assert iter(values)

        for value in values:
            AssertInt32(value)

        self._filters.append(
            {'type': SPH_FILTER_VALUES, 'attr': attribute, 'exclude': exclude, 'values': values})

    def SetGeoAnchor(self, attrlat, attrlong, latitude, longitude):
        assert isinstance(attrlat, str)
        assert isinstance(attrlong, str)
        assert isinstance(latitude, float)
        assert isinstance(longitude, float)
        self._anchor['attrlat'] = attrlat.encode('utf-8')
        self._anchor['attrlong'] = attrlong.encode('utf-8')
        self._anchor['lat'] = latitude
        self._anchor['long'] = longitude

    def Query(self, query, index='*', comment=''):
        """
        Connect to searchd server and run given search query.
        Returns None on failure; result set hash on success (see documentation for details).
        """
        assert(len(self._reqs) == 0)
        self.AddQuery(query, index, comment)
        results = self.RunQueries()
        self._reqs = []  # we won't re-run erroneous batch

        if not results or len(results) == 0:
            return None
        self._error = results[0]['error']
        self._warning = results[0]['warning']
        if results[0]['status'] == SEARCHD_ERROR:
            return None
        return results[0]

    def AddQuery(self, query, index='*', comment=''):
        """
        Add query to batch.
        """
        # build request
        req = QueryRequest()
        req.append(struct.pack('>4L', self._offset, self._limit, self._mode, self._ranker))
        if self._ranker == SPH_RANK_EXPR:
            req.append(struct.pack('>L', len(self._rankexpr)))
            req.append(self._rankexpr)
        req.append(struct.pack('>L', self._sort))
        req.append(struct.pack('>L', len(self._sortby)))
        req.append(self._sortby)

        req.append(struct.pack('>L', len(query)))
        req.append(query)

        req.append(struct.pack('>L', len(self._weights)))
        for w in self._weights:
            req.append(struct.pack('>L', w))
        req.append(struct.pack('>L', len(index)))
        req.append(index)

        req.append(struct.pack('>L', 1))  # id64 range marker
        req.append(struct.pack('>Q', self._min_id))
        req.append(struct.pack('>Q', self._max_id))

        # filters
        req.append(struct.pack('>L', len(self._filters)))
        for f in self._filters:
            req.append(struct.pack('>L', len(f['attr'])) + f['attr'].encode('utf-8'))
            filtertype = f['type']
            req.append(struct.pack('>L', filtertype))
            if filtertype == SPH_FILTER_VALUES:
                req.append(struct.pack('>L', len(f['values'])))
                for val in f['values']:
                    req.append(struct.pack('>q', val))
            elif filtertype == SPH_FILTER_RANGE:
                req.append(struct.pack('>2q', f['min'], f['max']))
            elif filtertype == SPH_FILTER_FLOATRANGE:
                req.append(struct.pack('>2f', f['min'], f['max']))
            req.append(struct.pack('>L', f['exclude']))

        # group-by, max-matches, group-sort
        req.append(struct.pack('>2L', self._groupfunc, len(self._groupby)))
        req.append(self._groupby)
        req.append(struct.pack('>2L', self._maxmatches, len(self._groupsort)))
        req.append(self._groupsort)
        req.append(struct.pack('>LLL', self._cutoff, self._retrycount, self._retrydelay))
        req.append(struct.pack('>L', len(self._groupdistinct)))
        req.append(self._groupdistinct)

        # anchor point
        if len(self._anchor) == 0:
            req.append(struct.pack('>L', 0))
        else:
            attrlat, attrlong = self._anchor['attrlat'], self._anchor['attrlong']
            latitude, longitude = self._anchor['lat'], self._anchor['long']
            req.append(struct.pack('>L', 1))
            req.append(struct.pack('>L', len(attrlat)) + attrlat)
            req.append(struct.pack('>L', len(attrlong)) + attrlong)
            req.append(struct.pack('>f', latitude) + struct.pack('>f', longitude))

        # per-index weights
        req.append(struct.pack('>L', len(self._indexweights)))
        for indx, weight in self._indexweights.items():
            req.append(struct.pack('>L', len(indx)) + indx + struct.pack('>L', weight))

        # max query time
        req.append(struct.pack('>L', self._maxquerytime))

        # per-field weights
        req.append(struct.pack('>L', len(self._fieldweights)))
        for field, weight in self._fieldweights.items():
            req.append(struct.pack('>L', len(field)) + field + struct.pack('>L', weight))

        # comment
        if isinstance(comment, str):
            comment = comment.encode('utf-8')
        req.append(struct.pack('>L', len(comment)) + comment)

        # attribute overrides
        req.append(struct.pack('>L', len(self._overrides)))
        for v in self._overrides.values():
            req.extend((struct.pack('>L', len(v['name'])), v['name']))
            req.append(struct.pack('>LL', v['type'], len(v['values'])))
            for id, value in v['values'].iteritems():
                req.append(struct.pack('>Q', id))
                if v['type'] == SPH_ATTR_FLOAT:
                    req.append(struct.pack('>f', value))
                elif v['type'] == SPH_ATTR_BIGINT:
                    req.append(struct.pack('>q', value))
                else:
                    req.append(struct.pack('>l', value))

        # select-list
        req.append(struct.pack('>L', len(self._select)))
        req.append(self._select)

        # send query, get response
        req = b''.join(req)

        self._reqs.append(req)

    def RunQueries(self):
        """
        Run queries batch.
        Returns None on network IO failure; or an array of result set hashes on success.
        """
        if len(self._reqs) == 0:
            self._error = 'no queries defined, issue AddQuery() first'
            return None

        sock = self._Connect()
        if not sock:
            return None

        req = b''.join(self._reqs)
        length = len(req) + 8
        req = struct.pack(
            '>HHLLL',
            SEARCHD_COMMAND_SEARCH,
            VER_COMMAND_SEARCH,
            length,
            0,
            len(self._reqs)) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_SEARCH)
        if not response:
            return None

        nreqs = len(self._reqs)

        # parse response
        max_ = len(response)
        p = 0

        results = []
        for i in range(0, nreqs, 1):
            result = {}
            results.append(result)

            result['error'] = ''
            result['warning'] = ''
            status = struct.unpack('>L', response[p:p + 4])[0]
            p += 4
            result['status'] = status
            if status != SEARCHD_OK:
                length = struct.unpack('>L', response[p:p + 4])[0]
                p += 4
                message = response[p:p + length]
                p += length

                if status == SEARCHD_WARNING:
                    result['warning'] = message
                else:
                    result['error'] = message
                    continue

            # read schema
            fields = []
            attrs = []

            nfields = struct.unpack('>L', response[p:p + 4])[0]
            p += 4
            while nfields > 0 and p < max_:
                nfields -= 1
                length = struct.unpack('>L', response[p:p + 4])[0]
                p += 4
                fields.append(response[p:p + length])
                p += length

            result['fields'] = fields

            nattrs = struct.unpack('>L', response[p:p + 4])[0]
            p += 4
            while nattrs > 0 and p < max_:
                nattrs -= 1
                length = struct.unpack('>L', response[p:p + 4])[0]
                p += 4
                attr = response[p:p + length]
                p += length
                type_ = struct.unpack('>L', response[p:p + 4])[0]
                p += 4
                attrs.append([attr, type_])

            result['attrs'] = attrs

            # read match count
            count = struct.unpack('>L', response[p:p + 4])[0]
            p += 4
            id64 = struct.unpack('>L', response[p:p + 4])[0]
            p += 4

            # read matches
            result['matches'] = []
            while count > 0 and p < max_:
                count -= 1
                if id64:
                    doc, weight = struct.unpack('>QL', response[p:p + 12])
                    p += 12
                else:
                    doc, weight = struct.unpack('>2L', response[p:p + 8])
                    p += 8

                match = {'id': doc, 'weight': weight, 'attrs': {}}
                for i in range(len(attrs)):
                    if attrs[i][1] == SPH_ATTR_FLOAT:
                        match['attrs'][attrs[i][0]] = struct.unpack('>f', response[p:p + 4])[0]
                    elif attrs[i][1] == SPH_ATTR_BIGINT:
                        match['attrs'][attrs[i][0]] = struct.unpack('>q', response[p:p + 8])[0]
                        p += 4
                    elif attrs[i][1] == SPH_ATTR_STRING:
                        slen = struct.unpack('>L', response[p:p + 4])[0]
                        p += 4
                        match['attrs'][attrs[i][0]] = ''
                        if slen > 0:
                            match['attrs'][attrs[i][0]] = response[p:p + slen]
                        p += slen - 4
                    elif attrs[i][1] == SPH_ATTR_MULTI:
                        match['attrs'][attrs[i][0]] = []
                        nvals = struct.unpack('>L', response[p:p + 4])[0]
                        p += 4
                        for n in range(0, nvals, 1):
                            match['attrs'][attrs[i][0]]\
                                .append(struct.unpack('>L', response[p:p + 4])[0])
                            p += 4
                        p -= 4
                    elif attrs[i][1] == SPH_ATTR_MULTI64:
                        match['attrs'][attrs[i][0]] = []
                        nvals = struct.unpack('>L', response[p:p + 4])[0]
                        nvals = nvals / 2
                        p += 4
                        for n in range(0, nvals, 1):
                            match['attrs'][attrs[i][0]]\
                                .append(struct.unpack('>q', response[p:p + 8])[0])
                            p += 8
                        p -= 4
                    else:
                        match['attrs'][attrs[i][0]] = struct.unpack('>L', response[p:p + 4])[0]
                    p += 4

                decodedAttrs = {}
                for key, value in match['attrs'].items():
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    if isinstance(key, bytes):
                        key = key.decode('utf-8')
                    decodedAttrs[key] = value
                match['attrs'] = decodedAttrs
                result['matches'].append(match)

            result['total'], result['total_found'], result[
                'time'], words = struct.unpack('>4L', response[p:p + 16])

            result['time'] = '%.3f' % (result['time'] / 1000.0)
            p += 16

            result['words'] = []
            while words > 0:
                words -= 1
                length = struct.unpack('>L', response[p:p + 4])[0]
                p += 4
                word = response[p:p + length]
                p += length
                docs, hits = struct.unpack('>2L', response[p:p + 8])
                p += 8

                result['words'].append({'word': word, 'docs': docs, 'hits': hits})

        self._reqs = []
        return results

    def BuildExcerpts(self, docs, index, words, opts=None):
        """
        Connect to searchd server and generate exceprts from given documents.
        """
        if not opts:
            opts = {}

        assert isinstance(docs, list)
        assert isinstance(opts, dict)

        sock = self._Connect()

        if not sock:
            return None

        # fixup options
        opts.setdefault('before_match', '<b>')
        opts.setdefault('after_match', '</b>')
        opts.setdefault('chunk_separator', ' ... ')
        opts.setdefault('html_strip_mode', 'index')
        opts.setdefault('limit', 256)
        opts.setdefault('limit_passages', 0)
        opts.setdefault('limit_words', 0)
        opts.setdefault('around', 5)
        opts.setdefault('start_passage_id', 1)
        opts.setdefault('passage_boundary', 'none')

        # build request
        # v.1.0 req

        flags = 1  # (remove spaces)
        if opts.get('exact_phrase'):
            flags |= 2
        if opts.get('single_passage'):
            flags |= 4
        if opts.get('use_boundaries'):
            flags |= 8
        if opts.get('weight_order'):
            flags |= 16
        if opts.get('query_mode'):
            flags |= 32
        if opts.get('force_all_words'):
            flags |= 64
        if opts.get('load_files'):
            flags |= 128
        if opts.get('allow_empty'):
            flags |= 256
        if opts.get('emit_zones'):
            flags |= 512
        if opts.get('load_files_scattered'):
            flags |= 1024

        # mode=0, flags
        req = QueryRequest([struct.pack('>2L', 0, flags)])

        # req index
        req.append(struct.pack('>L', len(index)))
        req.append(index)

        # req words
        req.append(struct.pack('>L', len(words)))
        req.append(words)

        # options
        req.append(struct.pack('>L', len(opts['before_match'])))
        req.append(opts['before_match'])

        req.append(struct.pack('>L', len(opts['after_match'])))
        req.append(opts['after_match'])

        req.append(struct.pack('>L', len(opts['chunk_separator'])))
        req.append(opts['chunk_separator'])

        req.append(struct.pack('>L', int(opts['limit'])))
        req.append(struct.pack('>L', int(opts['around'])))

        req.append(struct.pack('>L', int(opts['limit_passages'])))
        req.append(struct.pack('>L', int(opts['limit_words'])))
        req.append(struct.pack('>L', int(opts['start_passage_id'])))
        req.append(struct.pack('>L', len(opts['html_strip_mode'])))
        req.append((opts['html_strip_mode']))
        req.append(struct.pack('>L', len(opts['passage_boundary'])))
        req.append((opts['passage_boundary']))

        # documents
        req.append(struct.pack('>L', len(docs)))
        for doc in docs:
            if isinstance(doc, str):
                doc = doc.encode('utf-8')
            assert(isinstance(doc, bytes))
            req.append(struct.pack('>L', len(doc)))
            req.append(doc)

        req = b''.join(req)

        # send query, get response
        length = len(req)

        # add header
        req = struct.pack('>2HL', SEARCHD_COMMAND_EXCERPT, VER_COMMAND_EXCERPT, length) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_EXCERPT)
        if not response:
            return []

        # parse response
        pos = 0
        res = []
        rlen = len(response)

        for i in range(len(docs)):
            length = struct.unpack('>L', response[pos:pos + 4])[0]
            pos += 4

            if pos + length > rlen:
                self._error = 'incomplete reply'
                return []

            res.append(response[pos:pos + length])
            pos += length

        return res


def AssertInt32(value):
    assert(isinstance(value, int))
    assert(value >= -2 ** 32 - 1 and value <= 2 ** 32 - 1)


class QueryRequest(list):

    def __init__(self, initial_values=None):
        super()
        if initial_values:
            for value in initial_values:
                if isinstance(value, str):
                    value = value.encode('utf-8')
                super().append(value)

    def append(self, elt):
        if isinstance(elt, str):
            elt = elt.encode('utf-8')
        super().append(elt)
