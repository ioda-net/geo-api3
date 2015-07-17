# -*- coding: utf-8 -*-

<%inherit file="base.mako"/>

<%def name="table_body(c, lang)">
    <tr><td class="cell-left">Identifiant</td>                 <td>${c['featureId']}</td></tr>
    <tr><td class="cell-left">Surface</td>           <td>${c['attributes']['surface'] or '-'}</td></tr>
    <tr><td class="cell-left">Commune</td>                <td>${c['attributes']['commune'] or '-'}</td></tr>
    <tr><td class="cell-left">Adresse</td>             <td>${c['attributes']['adresse'] or '-'}</td></tr>
</%def>