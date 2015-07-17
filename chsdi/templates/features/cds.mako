# -*- coding: utf-8 -*-

<%inherit file="base.mako"/>

<%def name="table_body(c, lang)">
    <tr><td class="cell-left">Identifiant</td>                 <td>${c['featureId']}</td></tr>
    <tr><td class="cell-left">Surface</td>           <td>${c['attributes']['surface'] or '-'}</td></tr>
    <tr><td class="cell-left">Type de sol</td>                <td>${c['attributes']['cds'] or '-'}</td></tr>
    <tr><td class="cell-left">Commune</td>             <td>${c['attributes']['commune'] or '-'}</td></tr>
</%def>