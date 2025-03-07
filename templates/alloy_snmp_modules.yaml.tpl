modules:
{{ range ls "weops/global/modules/snmp" }}{{ .Key | indent 2 }}:
{{ .Value | indent 4 }}
{{ end }}