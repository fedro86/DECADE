# Technical Note: An open source library for processing weather radar data (wradlib)

- **Authors, year, venue:** M. Heistermann, S. Jacobi, T. Pfaff, 2013, *Hydrology and Earth System Sciences* 17, 863–871
- **Link:** [10.5194/hess-17-863-2013](https://doi.org/10.5194/hess-17-863-2013)
- **Access:** open, CC BY 3.0 (article). wradlib software: MIT License (paper Sect. 2.4 and current docs). wradlib notebooks and documentation: CC BY-SA 4.0 (current docs front page).
- **Read:** full text; wradlib documentation for `wradlib.classify.filter_gabella` (with `filter_gabella_a`, `filter_gabella_b`, the Gabella notebook) and `wradlib.classify.histo_cut` (API page and histo_cut notebook, docs 2.0.0) (read on 9/11/2026). The "latest" docs showed release 2.10.0.dev1 (dated 2026-10-30). Second source: wradlib developers, wradlib documentation, https://docs.wradlib.org (accessed 9/11/2026).

## What it is

A short software paper that introduces wradlib, a free, open-source Python library for weather radar processing. It describes design goals (modular library, Python, community project) and shows the modules by example: data reading, clutter detection, attenuation, georeferencing, compositing, gauge adjustment and verification. It gives no validation of the clutter filters. It is the reference that the wradlib docs ask users to cite.

## Numbers we use

**From the paper (2013)**

- Module `wradlib.clutter` (Table 1): clutter identification by two methods. (1) The Gabella and Notarpietro (2002) filter. (2) A method "based on statistics of accumulated precipitation". The paper does not name the second function or give its parameters.
- `wradlib.clutter.filter_gabella(data, tr1=12, n_p=6, tr2=1.1)` (Sect. 3.2, Example 2): call on a polar single-radar PPI (DWD Tuerkheim, DX format). These are example values, not defaults. The paper says that omitted parameters take default values, usually those of the original publication. It does not list the defaults.
- Output of the Gabella filter (Sect. 3.2): a Boolean clutter map. The paper then fills flagged bins by interpolation from neighbouring bins (`wradlib.ipol.interpolate_polar`, Example 3). This step is for polar data.
- `wradlib.zr.z2r` defaults a = 200, b = 1.6 (Sect. 3.3). Not a QC parameter; listed only because it is a stated default.
- No other QC functions are described. Beam blockage is mentioned only as a visible artefact in Fig. 3 (Manila, S-band radar shielded by Mount Natib). Attenuation correction exists (`wradlib.atten`) but is not relevant to a 2D composite.
- Licence of the software: MIT (Sect. 2.4).

**From the current documentation (read 9/11/2026)**

- Module rename: the clutter functions now sit in `wradlib.classify`, not `wradlib.clutter` (compare paper Example 2 with the current API pages).
- `wradlib.classify.filter_gabella(obj, *, wsize=5, **kwargs)` (API page and module source). Targets fixed ground clutter, isolated echoes and spikes: pixels with strong gradients to their neighbours, and echoes that are small or thin. Defaults from source: `wsize=5`, `thrsnorain=0.0`, `tr1=6.0`, `n_p=6`, `tr2=1.3`, `rm_nans=True`, `radial=False`, `cartesian=False`. The API page lists the keyword names but gives no defaults or meaning for `thrsnorain`, `tr1`, `n_p` and `tr2`; we read those from the module source. Output: Boolean array, True = clutter.
- Test 1, `filter_gabella_a(obj, wsize, tr1, *, cartesian=False, radial=False)` (API page, source). For each pixel it counts the neighbours in the window that are less than `tr1` below the centre value (source: `(obj - refr) < tr1`, count starts at −1 to exclude the centre). `filter_gabella` flags a pixel when this count is below `n_p`. So a pixel with few similar neighbours is flagged. `radial=True` checks only along range. `tr1` is in the units of the input (dB if the input is dBZ).
- Test 2, `filter_gabella_b(obj, *, thrs=0.0)` (API page, source). It labels contiguous echo regions above `thrs` (no-rain threshold) and computes, for each pixel, area / boundary length of its region. `filter_gabella` flags pixels where this ratio is below `tr2`. This catches small or elongated echoes. Non-rain pixels get 0.
- Combination (source): clutter = test 1 OR test 2.
- NaN handling (source): with `rm_nans=True` NaNs are set to +inf before filtering. With `False`, counts are scaled by the fraction of valid pixels in the window.
- Input of `filter_gabella`: a single image (one scan), 2D array. Polar is assumed; Cartesian needs `cartesian=True` (API page). The notebook runs it on one polar sweep of uncorrected reflectivity in dBZ (GAMIC file, 360 azimuths × 1000 gates).
- Gabella notebook (docs 2.9.5, "Clutter detection using the Gabella approach"): `filter_gabella(wsize=5, thrsnorain=0.0, tr1=6.0, n_p=8, tr2=1.3)`. Note `n_p=8` here, not the default 6.
- `wradlib.classify.histo_cut(obj, *, upper_frequency=0.01, lower_frequency=0.01)` (API page, source). Targets static clutter (persistently high totals) and shading or beam blockage (persistently low totals). It does not target single-time artefacts.
- `histo_cut` method (API page, source): histogram of the accumulation with 50 bins on raw values, no log. Classes whose frequency is below the set fraction of the most frequent class are cut from the upper and lower tails. This repeats until both bounds change by 1 or less (in input units). Defaults 0.01 for both tails.
- `histo_cut` input (API page): a 2D spatial array of accumulated rain. The docs recommend "one year" as the accumulation period. The notebook says months to a year. The function itself makes no polar/Cartesian assumption; the notebook uses an annual rainfall sum of DWD radar Feldberg.
- `histo_cut` output (API page): uint8 array. 1 = clutter, 2 = shading, 0 = other. The docs warn that users who need a Boolean mask must cast it.
- `histo_cut` notebook (docs 2.0.0): mentions values around 0.05 for European ODIM_H5 data and refers to the EURADCLIM paper, which indeed used 5% instead of the 1% default (Overeem et al. 2023, section 3.3).
- **Checked in the installed package** (wradlib 2.9.8, 9/11/2026): the signatures and defaults above are the same; `wsize` is the full window width (the window runs from −`wsize`//2 to +`wsize`//2), so `wsize=5` is a 5 × 5 window, 10 km × 10 km on the 2 km OPERA grid.
- Citation (docs front page): cite Heistermann et al. (2013); for a specific version cite Zenodo doi:10.5281/zenodo.1209843.

## Relevance to DECADE

It informs H2, the choice of the first QC filters on the OPERA ODYSSEY composite. It is the software source for the two functions EURADCLIM used. `filter_gabella` with `cartesian=True` can run on each 15 min composite image to flag spikes and isolated or thin echoes. `histo_cut` can run on the annual (or multi-year) accumulation of the composite over Belgium, 2012–2024, to flag fixed clutter (class 1) and blocked or shaded areas (class 2). The docs give the exact current names, defaults and input types, so the H2 code can state them. Any change from the defaults (for example `n_p=8` or 0.05 frequencies) must be justified from Overeem et al. (2023) or Gabella and Notarpietro (2002), not from this paper.

## Limits

- The paper is a software note. It gives no validation, error rates or tuning advice for the clutter filters.
- The paper's example values (tr1=12, n_p=6, tr2=1.1) differ from the current defaults (tr1=6.0, n_p=6, tr2=1.3). The paper does not explain them.
- The Gabella defaults come from single-radar polar data in mountainous terrain. Our data is a 2 km Cartesian composite of many radars over flat terrain. Window size is in pixels, so the physical window depends on the grid (5 × 5 pixels, as checked in the package).
- `tr1` works on input units. It assumes dBZ; on rain rates it would mean something different.
- The composite is already processed by OPERA. Some clutter may be removed, and composite edges or overlaps can create gradients that the Gabella filter may flag.
- `histo_cut` needs a long-term sum. It finds only persistent artefacts. It does not remove interference spikes or single-time false echoes. Thresholds are relative to the most frequent class, so they depend on domain size and the rain climate of the period.
- Neither source addresses echoes without rain at the ground (for example anaprop or birds) as a separate class. Radial interference lines are not named as a target; the `radial` option of test 1 exists, but its use for spikes is not documented.
- The docs describe the "latest" development version (2.10.0.dev1). Defaults may change between releases. We must record the wradlib version we install.
