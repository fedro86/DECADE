# Review and discussion of homogenisation methods for climate data

- **Authors, year, venue:** Ribeiro, S., Caineta, J., Costa, A. C., 2016. Physics and Chemistry of the Earth 94, 167–179.
- **Link:** [10.1016/j.pce.2015.08.007](https://doi.org/10.1016/j.pce.2015.08.007)
- **Access:** the journal version is paywalled (Elsevier); the peer-reviewed accepted manuscript is open in the [NOVA University Lisbon repository (RUN)](https://run.unl.pt/handle/10362/76624) under CC BY-NC-ND 4.0, and is the PDF kept here. Page numbers below are those of the manuscript.
- **Read:** parts of the accepted manuscript: section 2 (approaches, absolute and relative methods, multiple breakpoints), section 3.1–3.2 (non-parametric and classical tests), the SNHT and RHtests paragraphs of sections 3.5 and 4, and section 6 (conclusions). The rest (regression and Bayesian methods, other software, the HOME summary, Table 1 and the supplementary table) was not read.

## What it is

A literature review of homogenisation methods for climate series: it sorts detection and correction techniques into non-parametric tests, classical tests, regression models, Bayesian approaches and full homogenisation procedures (SNHT, MASH, PRODIGE, ACMANT, USHCN, HOMER and others), says what each assumes and does, and summarises the comparison studies, with an emphasis on precipitation.

## Numbers we use

The paper gives no thresholds or power values; it is used for what it says each test assumes.

- **Relative series:** section 2.2 (p. 8). Relative methods work on composite series of differences (temperature, pressure) or ratios (precipitation) between candidate and reference stations; absolute methods cannot tell a natural from an artificial change without station history (p. 8).
- **Wilcoxon–Mann–Whitney for non-normal data:** section 3.1 (p. 12). The rank-based Wilcoxon–Mann–Whitney test is advised when normality is in doubt, as for precipitation; normality is easier to reach for yearly or accumulated totals than for monthly values.
- **Pettitt's test locates an unknown break:** section 3.1 (pp. 12–13). Pettitt's test is a rank test derived from Mann–Whitney that finds the most likely date of a single break; it is more sensitive to breaks in the middle of the series.
- **Von Neumann ratio:** section 3.1 (p. 11). The ratio of the mean square of successive differences to the variance, closely related to the lag-1 serial correlation; it flags irregularity but gives no date.
- **SNHT:** section 3.5 (pp. 18–19). SNHT (Alexandersson, 1986) builds a ratio or difference series against a reference assumed homogeneous, standardises it, and compares the means before and after each possible date against a critical value, i.e. it searches for the date.
- **Autocorrelation and seasonality in RHtests:** section 4 (pp. 22–23). The penalised maximal t test (PMT, with reference series) and F test (PMF, without) of RHtests estimate the annual cycle, linear trend and autocorrelation iteratively while accounting for the detected shifts (Wang, 2008).
- **Monthly is harder than annual:** section 6 (p. 30). Among the conclusions taken from the comparison studies: annual data sets are homogenised better than monthly ones, possibly because variability grows with temporal resolution; precipitation homogenisation needs more work.

## Relevance to DECADE

H3 (#20), step of the monthly radar / ERA5-Land ratio at 7/2024 and 9/2024 (`opera_ds/homog.py`, `step`).

- **Rank test as the check on the t-test.** Monthly precipitation ratios may not be normal even in log; the review advises the Wilcoxon–Mann–Whitney test in that case (p. 12). Applied to the months before and after a known date, it is the rank counterpart of the two-sample t-test recommended by the WMO guidelines (see the 2020 WMO summary, p. 33). Running both and reporting both is a direct use of this; neither handles autocorrelation, and the review gives no correction.
- **Pettitt and SNHT answer a different question.** Both search for the most likely date (pp. 12–13, 18–19). With dates fixed in advance from metadata they are not the primary test; they can be run afterwards as a check that the series does not point to a different date.
- **Open source for SNHT.** The description of Alexandersson (1986) here (pp. 18–19) is what this repository relies on; the original (J. Climatol. 6, 661–675) is paywalled and was not read.
- **Not settled:** significance level, power or detectable step for short series, and how to correct either test for autocorrelation and seasonality of monthly ratios.

## Limits

- **A review:** it describes tests from the cited literature without new results or numbers; statements are only as precise as the sources it summarises.
- **Station homogenisation:** long series and networks of gauges; nothing on a radar–reanalysis pair or on series of a few years.
- **Partly read** (see Read); the regression, Bayesian and software sections may contain points not reflected here.
- **Accepted manuscript,** not the typeset version: page numbers differ from the journal.
