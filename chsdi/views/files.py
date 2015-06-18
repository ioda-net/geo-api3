# -*- coding: utf-8 -*-

import os
import os.path
import uuid
import base64
from datetime import datetime

from pyramid.view import view_config, view_defaults
import pyramid.httpexceptions as exc
from sqlalchemy.orm.exc import NoResultFound
from pyramid.response import Response

from chsdi.lib.decorators import validate_kml_input
from chsdi.models.utilities import Files


@view_defaults(renderer='jsonp', route_name='files')
class FileView(object):

    def __init__(self, request):
        self.request = request
        self.query = request.db.query
        self.db = request.db
        self.kml_storage_path = request.registry.settings['kml.storage_path']
        if request.matched_route.name == 'files':
            self.admin_id = None
            self.key = None
            id = request.matchdict['id']
            if self._is_admin_id(id):
                self.admin_id = id
                self.file_id = self._get_file_id_from_admin_id()
            else:
                self.file_id = id

    def _is_admin_id(self, id):
        return self.query(Files)\
            .filter(Files.admin_id == id)\
            .count() > 0

    def _get_file_id_from_admin_id(self):
        return self._get_file_from_admin_id().file_id

    def _get_file_from_admin_id(self):
        try:
            return self.query(Files)\
                .filter(Files.admin_id == self.admin_id)\
                .one()
        except NoResultFound:
            raise exc.HTTPNotFound('File %s not found' % self.admin_id)

    def _get_uuid(self):
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', '')

    @view_config(route_name='files_collection', request_method='OPTIONS', renderer='string')
    def options_files_collection(self):
        # TODO: doesn't seem to be applied
        self.request.response.headers.update({
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'true'})
        return ''

    @view_config(route_name='files_collection', request_method='POST')
    @validate_kml_input()
    def create_file(self):
        self.file_id = self._get_uuid()
        self.admin_id = self._get_uuid()
        data = self.request.body
        mime_type = self.request.content_type

        self._save_kml(data, mime_type)

        return {'adminId': self.admin_id, 'fileId': self.file_id}

    def _get_save_path(self):
        return os.path.join(self.kml_storage_path, self.file_id) + '.kml'

    def _save_kml(self, data, mime_type, update=False):
        with open(self._get_save_path(), 'w') as kml:
            kml.write(data)

        if not update:
            file = Files(
                admin_id=self.admin_id,
                file_id=self.file_id,
                mime_type=mime_type,
                createtime=datetime.now()
            )
            self.db.add(file)
            self.db.commit()

    @view_config(request_method='GET')
    def read_file(self):
        try:
            if self.admin_id is not None:
                return {'fileId': self.file_id}
            else:
                with open(self._get_save_path()) as kml:
                    data = kml.read()
                return Response(data, content_type='application/vnd.google-earth.kml+xml')
        except Exception as e:
            print(e)
            raise exc.HTTPNotFound('File %s not found' % self.file_id)

    @view_config(request_method='POST')
    @validate_kml_input()
    def update_file(self):
        data = self.request.body
        mime = self.request.content_type

        if self.admin_id is not None:
            try:
                self._save_kml(data, mime, update=True)

                return {'adminId': self.admin_id, 'fileId': self.file_id, 'status': 'updated'}
            except:
                raise exc.HTTPInternalServerError('Cannot update file with id=%s' % self.admin_id)
        else:
            # Fork file, get new file ids
            self.file_id = self._get_uuid()
            self.admin_id = self._get_uuid()

            del self.key

            self._save_to_s3(data, mime)

            return {'adminId': self.admin_id, 'fileId': self.file_id, 'status': 'copied'}

    @view_config(request_method='DELETE')
    def delete_file(self):
        if self.admin_id is not None:
            try:
                self._delete_file()
                return {'success': True}
            except:
                raise exc.HTTPInternalServerError('Error while deleting file %s' % self.file_id)
        else:
            raise exc.HTTPUnauthorized('You are not authorized to delete file %s' % self.file_id)

    def _delete_file(self):
        file = self._get_file_from_admin_id()
        self.db.delete(file)
        os.remove(self._get_save_path())
        self.db.commit()

    @view_config(request_method='OPTIONS', renderer='string')
    def options_file(self):
        # TODO: doesn't seem to be applied
        self.request.response.headers.update({
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'true'})
        return ''
