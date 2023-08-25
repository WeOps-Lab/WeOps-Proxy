groups:
- name: weops
  rules:{{ range ls "/weops/global/alerts/strategy" }}{{ with $d := .Value | parseYAML }}
  - alert: "{{ $d.alert }}"
    expr: "{{ $d.expr }}"
    for: "{{ $d.for }}"
    labels: 
      {{ range $i, $elem := $d.labels }}"{{$elem.name}}": "{{$elem.value}}"
      {{ end }}
    annotations:
      {{ range $i, $elem := $d.annotations }}"{{$elem.name}}": "{{$elem.value}}"
      {{ end }}

{{ end }}{{ end }}