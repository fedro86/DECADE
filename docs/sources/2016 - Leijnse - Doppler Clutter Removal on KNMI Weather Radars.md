# Doppler Clutter Removal on KNMI Weather Radars

- **Authors, year, venue:** Hidde Leijnse, Hans Beekhuis, Iwan Holleman, 2016 (dated 5 January 2016). KNMI Technical Report TR-355, De Bilt (PDF of 40 pages including covers).
- **Link:** [cdn.knmi.nl TR355.pdf](https://cdn.knmi.nl/knmi/pdf/bibliotheek/knmipubTR/TR355.pdf); catalogue page: [knmi.nl publication page](https://knmi.nl/research/publications/doppler-clutter-removal-on-knmi-weather-radars)
- **Access:** free PDF from KNMI; no licence stated.
- **Read:** full text (all 5 chapters); figures from their captions only; the cloud-mask histograms (Fig. 4.5, 4.6) have no numbers in the text.

## What it is

KNMI compares its own statistical (fluctuation-based) clutter filter, used on the lowest 0.3° elevation, with the standard time-domain Doppler filter used on the 0.4° elevation of its two C-band radars (De Bilt and Den Helder), with and without a 1-D speckle filter. The comparison uses a severe anaprop case (30 March 2014), a rain case (7 April 2014), an objective 10-day check against the Meteosat NWC SAF cloud mask, and IQ-replay tests. It concludes that Doppler filtering plus a speckle filter should replace the statistical scheme, and that sea clutter remains the weak point of both methods.

## Numbers we use

- 40 %: share of sea clutter the original statistical scheme removes, while anaprop clutter over land is removed almost completely (Sect. 2.1, citing Wessels and Beekhuis 1992, 1994).
- ~45 %: share of clutter signals detected by the single-sample fluctuation test alone, before spatial processing (Sect. 2.1.1).
- 4.2 dB vs 2.0 dB: peaks of the standard deviation of raw power for rain and for clutter; theory gives 5.5 dB for rain (Sect. 2.1.1, Fig. 2.1).
- 14 km: the statistical filter removes nothing closer than this to the radar (Sect. 4.1.1, Ch. 5).
- 10–20 dB: typical maximum clutter correction ratio of a Doppler filter; above it the bin is rejected, i.e. data with 90–99 % clutter power can still be reconstructed (Sect. 2.2.1).
- ≥ 32 samples per range bin: typical minimum for frequency-domain Doppler filters (Sect. 2.2.1); in the IQ-replay test only 14 pulses were available against 28 for the time-domain filter, because of dual-PRF switching inside a 1° sector (Sect. 4.3).
- > 5 dB loss near the zero isodop, i.e. rain rate reduced by a factor ≥ 3 with Marshall–Palmer; > 1 dB (≈ 15 % rain rate) elsewhere, for the time-domain Doppler filter in rain (Sect. 4.1.2).
- 0.3° vs 0.4°: elevations compared, ~25 s apart, beam width ~1° (Sect. 3.2, Ch. 4; Table 3.1). Lowest scan: PRF 250 Hz, range 320 km, statistical filter; 0.4°: PRF 600/450 Hz, 240 km, time-domain Doppler.
- 14 elevations every 5 min (288 volumes per day) since the 2006 Digital Radar Upgrade (Sect. 3.1, Fig. 3.1).
- 30 March – 8 April 2014: 10-day verification period with frequent anaprop and several rain events; reference = NWC SAF cloud mask (Derrien and Le Gléau 2005); score = area of non-zero radar echoes in cloud-free pixels; low-level PPI scores use only ranges ≥ 15 km (Sect. 3.2, 4.2, Fig. 4.6 caption).
- 30 March 2014, 06:00 UTC: severe anaprop with intense land and sea clutter over the Netherlands (Sect. 4.1.1).
- 1500 m: height of KNMI's operational pseudo-CAPPI composite (Sect. 4.1.1).

## Relevance to DECADE

H2 (#19), sea clutter and anomalous propagation:

- **Upstream removal (KNMI):** both KNMI filters struggle with sea clutter. The statistical filter fails because sea clutter in anaprop is widespread rather than speckled; the Doppler filter fails because waves move, so sea echoes are not at zero velocity (Sect. 4.1.1, 4.2). The report states that effectiveness against intense sea clutter "is limited due to the variability of the sea surface" (Ch. 5). For the Den Helder radar, where much of the clutter is sea clutter, the statistical filter beat the Doppler filter in the cloud-mask test. So residual sea clutter in the Dutch contribution to the OPERA composite over the North Sea is expected, especially in anaprop spells, and probably more before the KNMI radar replacement (RASER project; installation of new dual-pol radars "foreseen in 2016", Ch. 1).
- **Recommended fixes (upstream, not on composites):** stricter clutter settings over sea than over land via a land–sea mask, either in the signal processor or as post-processing of volume data; polarimetric clutter detection on the new radars; frequency-domain Doppler filtering with single PRF (Ch. 5). The land–sea split is an idea we can reuse on the composite: a stricter clutter test over sea pixels only.
- **Satellite data:** the cloud mask is used only as a verification tool ("no cloud, no rain"), not as a filter, and it works on both single-radar PPIs and on the pseudo-CAPPI composite (Fig. 4.5). This is directly transferable to DECADE as a diagnostic: count composite echoes in cloud-free NWC SAF pixels over the sea per month or year.
- **Speckle filter:** a 1-D speckle filter added after Doppler filtering gives a large gain and hardly harms rain (Sect. 4.1.2, Ch. 5). A 2-D speckle (isolated-pixel) filter is one of the few tools that can be applied on a composite grid.
- **Input each method needs:** statistical filter: raw power samples per pulse (IQ level); Doppler filter: IQ time series, PRF settings; speckle filter: any reflectivity field; cloud-mask check: NWC SAF cloud mask collocated in time and space.

## Limits

- Dutch radars (De Bilt, Den Helder) only; Jabbeke and the Belgian coast are not discussed.
- Signal-processing filters need raw data at the radar; they cannot be run on the OPERA ODYSSEY maximum-reflectivity composite.
- Results are for one 10-day spring period in 2014 and two cases; the cloud-mask results are given only as histograms, without numbers in the text.
- The comparison assumes the 0.3° and 0.4° scans differ only in the filter; the report itself shows this is not always true (different PRF, pulse length 2.0 vs 0.8 µs), especially over the sea south-west of Den Helder.
- Small inconsistency in the report: Ch. 5 says IQ data were reprocessed from the De Bilt radar, while Sect. 4.3 shows Den Helder IQ data.
- Recommendations are plans as of January 2016; the report does not say what KNMI actually implemented afterwards.
