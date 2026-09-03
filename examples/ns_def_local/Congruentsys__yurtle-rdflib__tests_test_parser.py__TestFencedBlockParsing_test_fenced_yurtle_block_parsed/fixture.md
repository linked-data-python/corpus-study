---
id: EXP-981
title: "Y0/Y1 Chunk Graph Storage"
type: expedition
status: done
tags: [ylayer, knowledge]
---

# EXP-981: Y0/Y1 Chunk Graph Storage

Implementation of chunk-level graph storage for Y0/Y1 layers.

```turtle
@prefix ylayer: <https://nusy.dev/ylayer/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<#chunk-storage> a ylayer:Feature ;
    rdfs:label "Chunk Graph Storage" ;
    ylayer:layer "Y0", "Y1" .
```

## Results

The feature was implemented successfully.

```yurtle
@prefix kb: <https://yurtle.dev/kanban/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> kb:statusChange [
    kb:status kb:done ;
    kb:at "2026-02-25T23:46:48"^^xsd:dateTime ;
    kb:by "DGX" ;
  ] .
```
