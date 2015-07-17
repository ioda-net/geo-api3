# -*- coding: utf-8 -*-

<%inherit file="base.mako"/>

<%def name="table_body(c, lang)">
    <tr><td class="cell-left">Identifiant</td>                 <td>${c['featureId']}</td></tr>
    <tr><td class="cell-left">Surface</td>           <td>${c['attributes']['surface'] or '-'}</td></tr>
    <tr><td class="cell-left">Rayonnement</td>                <td>${c['attributes']['rayonnement'] or '-'}</td></tr>
    <tr><td class="cell-left">Orientation</td>                <td>${c['attributes']['orientation'] or '-'}</td></tr>
    <tr><td class="cell-left">Pente</td>                <td>${c['attributes']['pente'] or '-'}</td></tr>
</%def>