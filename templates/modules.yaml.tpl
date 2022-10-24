{{ range ls "weops/global/modules/snmp" }}{{ .Key }}:
{{ .Value | indent 1}}
{{ end }}