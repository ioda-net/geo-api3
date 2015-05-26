# -*- coding: utf-8 -*-

<%
  c = legend['layer']
  hasLegend = legend['hasLegend']
  legendUrl = legend['legendUrl']
  host = h.make_agnostic(request.host_url + request.uscript_name)
  lang = request.lang
  times = c['attributes']['dataStatus'] if 'dataStatus' in c['attributes'] else '-'
%>
<div class="legend-container">
<div class="legend-header">
% if 'dataOwner' in c['attributes']:
  <p class='bod-title'><span>${c['fullName'] or '-'}</span> (${c['attributes']['dataOwner'] or '-'})</p>
% endif
% if 'abstract' in c['attributes']:
  <p class='legend-abstract'>${c['attributes']['abstract'] or '-'|n}</p>
% endif
</div>
<div class="legend-footer">
% if hasLegend:
  <br>
  <span>${_('Legend')}</span><br>
  <div class="img-container">
    <img src=${legendUrl} alt="layer legend img"/>
  </div>
  <br><br>
% endif
  <span>${_('Information')}</span><br>
  <table>
    <tr><td>${_('geobasisdatensatz')}</td> <td>${c['attributes']['bundCollectionNumber'] if 'bundCollectionNumber' in c['attributes'] else '-'}</td></tr>
% if 'scaleLimit' in c['attributes']:
    <tr><td>${_('Gueltiger Massstabsbereich')}</td> <td>${c['attributes']['scaleLimit']}</td></tr>
% endif
    <tr><td>${_('Metadaten')}</td>
% if 'idGeoCat' in c:
  % if lang in ('de', 'rm'):
      <td><a target="_blank" href="http://www.geocat.ch/geonetwork/srv/deu/metadata.show?uuid=${c['idGeoCat']}&currTab=simple">
  % elif lang in ('fr', 'it'):
      <td><a target="_blank" href="http://www.geocat.ch/geonetwork/srv/fra/metadata.show?uuid=${c['idGeoCat']}&currTab=simple">
  % else:
      <td><a target="_blank" href="http://www.geocat.ch/geonetwork/srv/eng/metadata.show?uuid=${c['idGeoCat']}&currTab=simple">
  % endif
      ${_('layer_geocat_text')}</a></td>
% else:
      <td>-</td>
% endif
    </tr>
    <tr>
      <td>${_('Detailbeschreibung')}</td>
% if 'urlDetails' in c['attributes']:
      <td><a href="${c['attributes']['urlDetails']}" target="new">${_('layer_url_text')}</a></td>
% else:
      <td>-</td>
% endif
    </tr>
    <tr>
      <td>${_('Datenbezug')}</td>
% if 'downloadUrl' in c['attributes']:
      <td><a href="${c['attributes']['downloadUrl']}" target="new">${_('layer_url_download_text')}</a></td>
% else:
      <td>-</td>
% endif
    </tr>
    <tr>
      <td>${_('Thematisches Geoportal')}</td>
% if 'urlApplication' in c['attributes']:
      <td><a href="${c['attributes']['urlApplication']}" target="new">${_('layer_url_portal_text')}</a></td>
% else:
      <td>-</td>
% endif
    </tr>
    <tr>
      <td>${_('WMS Dienst')}</td>
% if 'wmsUrlResource' in c['attributes']:
      <td><a href="${c['attributes']['wmsUrlResource']}" target="new">${_('wms_resource_text')}</a></td>
% else:
      <td>-</td>
% endif
    </tr>
    <tr>
      <td>${_('Datenstand')}</td>
% if times:
  % if len(times) == 4:
      <td>${times}</td>
  % elif len(times) == 6:
      <td>${times[4:]}.${times[:4]}</td>
  % elif len(times) == 8:
      <td>${times[6:]}.${times[4:6]}.${times[:4]}</td>
  % elif len(times) == 9:
      <td>${times}</td>
  % elif len(times) ==13:
      <td>${times[4:6]}.${times[:4]}-${times[11:]}.${times[7:11]}</td>
  % elif len(times) ==17:
      <td>${times[6:8]}.${times[4:6]}.${times[:4]}-${times[15:]}.${times[13:15]}.${times[9:13]}</td>
  % endif
% else:
      <td>-</td>
% endif
    </tr>
  </table>
</div>
</div>
