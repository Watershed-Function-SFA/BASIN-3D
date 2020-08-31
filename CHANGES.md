# BASIN-3D Releases



## v3.0.1 (Bug Fix)
This release contains a single bug fix

+ Issue #56 - Make utc offset in measTVPobs required so that 0 is not dropped
    

## v3.0.0 (Beta)
Refactor to use basin3d-core.  Functionality was removed but no existing functionaly changes.
Major release due to the fact that the changes are not backwards compatible due to
and api path change and some minor api model changes.

+ Renames Django app (basin3d -> django_basin3d)
+ Adds basin3d catalog for Django Models
(django_basin3d.catalog.CatalogDjango)
+ Refactored Djangod Models, Views and Viewsets to fit with
  basin3d-core interfaces
+ removed all refereces to direct api -> removing /synthesis for
endpoint
+ ReadOnly Serializers - Converts all serializers to read-only
  This will optimize the performance slighlty.
  We don't need the serializers to be writable anyway.
+ Consolidate migrations scripts - handles Operational Error in initialization of CatalogDjango.  This will
    happend when the migration is reveresed.



## v2.0.0 (Beta)
Second prototype release of BASIN-3D. 
Refactored synthesis model to more closely follow OGC observation and measurement standards
Refactored REST API


## v1.0.0 (Alpha)

First prototype release of BASIN-3D. 
Demonstrates data synthesis across multiple data sources.





