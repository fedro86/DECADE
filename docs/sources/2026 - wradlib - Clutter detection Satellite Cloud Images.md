# Clutter detection - Satellite Cloud Images (wradlib notebook)

- **Authors, year, venue:** wradlib developers, wradlib documentation, notebook `notebooks/classify/clutter/clutter_cloud` (current docs version 2.10.0, retrieved 9 November 2026; the MyST source is identical to version 2.9.3). Older 1.x title: "Clutter detection by using space-born cloud images" (`wradlib_clutter_cloud_example`). The function used is `wradlib.classify.filter_cloudtype` (in 1.x: `wradlib.clutter.filter_cloudtype`).
- **Link:** [docs.wradlib.org latest notebook](https://docs.wradlib.org/en/latest/notebooks/classify/clutter/clutter_cloud.html); source: [clutter_cloud.md](https://docs.wradlib.org/en/latest/_sources/notebooks/classify/clutter/clutter_cloud.md); old version: [1.19.1 notebook](https://docs.wradlib.org/en/1.19.1/notebooks/classify/wradlib_clutter_cloud_example.html); function code: [wradlib/classify.py on GitHub](https://github.com/wradlib/wradlib/blob/main/wradlib/classify.py).
- **Access:** open. Notebooks and docs CC BY-SA 4.0, source code MIT (wradlib LICENSE.txt).
- **Read:** full notebook source and the code of `filter_cloudtype` and `util.filter_window_polar`.

## What it is

A short tutorial showing how to flag radar echoes as clutter where a collocated satellite cloud-type map says there is no cloud. It reads one NWC SAF MSG3 cloud-type (CT) file and one Belgian radar sweep, reprojects the radar bins into the satellite projection, takes the nearest satellite pixel for each bin, shrinks the cloud-free area by a window that accounts for advection and parallax, and marks as clutter every radar bin above a threshold that falls in what remains cloud-free.

## Numbers we use

- Example data: radar file `20130429043000.rad.bewid.pvol.dbzh.scan1.hdf` (Belgian radar Wideumont, `bewid`, 29 April 2013 04:30) and satellite file `SAFNWC_MSG3_CT___201304290415_BEL_________.h5` (NWC SAF cloud type, MSG3, 04:15, Belgian area), both from the wradlib-data repository (notebook, "Read" sections).
- Localisation error: `timelag = 9 * 60` s and `wind = 10` m/s, so `smoothing = 5400` m (section "Estimate localisation errors"). Note the two file timestamps differ by 15 min; the notebook does not explain the 9 min.
- `smoothing` is the half size of the window in metres; the cloud-free mask is passed through a minimum filter of that size, so a bin is called clutter only if the whole window around it is cloud-free (code of `filter_cloudtype` and `util.filter_window_polar`). Polar and Cartesian grids are both supported (`grid="polar"` or `"cartesian"`).
- Default rule: clutter = (CT is class 1 or 2) and (reflectivity > `thrs`, default 0). Optional switches add classes 3–4 (`snow`, land/sea snow), 5–7 (`low`, very low stratus, very low cumulus, low cumulus) and 14, 18 (`cirrus`, very thin cirrus and fractional clouds) to the "no precipitation" set (docstring and code). In the NWC SAF CT legend of that era classes 1 and 2 are cloud-free land and cloud-free sea; the code itself does not label them.
- Satellite-to-radar matching: nearest-neighbour (`map_coordinates_nearest`) after georeferencing the radar sweep into the satellite CRS; the notebook adds a fix because the MSG3 CT file has broken georeferencing.

## Relevance to DECADE

H2 (#19), sea clutter and anomalous propagation:

- **Satellite-based, works on any grid:** this is the simplest form of the "no cloud, no rain" idea also used by KNMI TR-355 (as verification) and by Bøvith et al. 2006 (as a classifier input). Because the function accepts a Cartesian grid, it can be applied directly to the OPERA 2 km composite over Belgium and the North Sea, given a collocated NWC SAF cloud-type (or cloud-mask) field every 15 min.
- **Good fit for anaprop sea clutter:** severe anaprop sea clutter tends to come with clear, high-pressure weather (as in Bøvith et al. 2006, Case I), which is when a cloud-free test is most useful. The notebook itself says nothing about anaprop or sea clutter. Ship and wind-farm echoes under clouds would not be caught.
- **Upstream vs composite:** the notebook uses a single-radar polar sweep from Wideumont, not Jabbeke and not a composite; nothing in it depends on polar data except the grid choice.
- **Input needed:** reflectivity field; NWC SAF CT (PGE02) or equivalent at matching time; reprojection; an estimate of time lag and cloud speed to set the smoothing window.

## Limits

- Tutorial only: one example, no verification, no false-alarm or missed-clutter statistics, no reference paper cited for the method.
- Hard-coded class numbers follow the old PGE02 cloud-type legend; for 2012–2024 data the NWC SAF product version (and its class table) must be checked before using the switches.
- A binary rule with threshold 0 by default: any echo in a cloud-free window is removed, which may delete real light rain if the satellite misses thin or low cloud, and keeps all clutter under cloud.
- Requires a 13-year archive of NWC SAF cloud type (or cloud mask) over Belgium at 15 min, which is not part of the OPERA data; availability and cost of that archive are not covered here.
- The 9-min time lag and 10 m/s wind are illustrative values, not tuned.
