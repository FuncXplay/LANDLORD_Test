# LANDLORD Algorithm Test

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4915858.svg)](https://doi.org/10.5281/zenodo.4915858) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/FuncXplay/LANDLORD_Test/HEAD)

Using Binder dataset, download `binder.sqlite` file into project folder first or use binder to access from jupyter-notebook (hmmmm... consider the large size of `binder.sqlite`, we don't expect it to work directly on jupyter-notebook so plz download it yourself😜).



### LANDLORD

Reuse larger containers in cache

When no larger containers to reuse, check Jacaard distance and, from those containers with a Jaccard distance no larger than ` ALPHA`, merge the container with the smallest Jaccard distance.

Already tested with 50000 requests with `ALPHA = 0.5` and `ALPHA = 0.3`

