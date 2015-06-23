# PhotoScan Python Scripts

A collection of useful python scripts for [PhotoScan](http://www.agisoft.com/)
adapted from http://wiki.agisoft.com/wiki/Python.

* [bbox2coords](bbox2coords.py): Creates a bounding box based on the
  coordinate system of the active chunk. Sides of the bbox are parallel
to the coordinate system axis.
* [coords2bbox](coords2bbox.py): Build a bounding box from the
  coordinate system.
* [copy_bounding_box](copy_bounding_box.py): Copies the bounding box
  from the active chunk to all other chunks in a project.
* [export_individual_orthophotos](export_individual_orthophotos.py):
  Export a set of orthophotos based on individual cameras.
* [masking_by_color](masking_by_color.py): Create masks for images based
  on user-selected color and tolerance.
* [split_in_chunks](split_in_chunks.py): Split the original chunk in to
  multiple chunks with smaller bounding boxes. Optionally, generate a
mesh/cloud and merge in to larger chunk.
