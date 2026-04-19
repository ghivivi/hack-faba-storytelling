# Faba Box Compatible NTAG21x FAQ

## NTAG2x3 family

FABA figures use NTAG203 chips, so ideally you should use those.
Since they are almost impossible to come by, you can also use NTAG213 chips, which are the same memory size and almost the same functionality.

Unfortunately getting the OEM chips from NXP is tricky and there are many knock-off chips that do not work.
Most of these behave as if the previously read chip was put on the FABA box regardless of their content, so be careful to turn the box off and on again before testing, otherwise you may wrongly assume they work.


## NTAG215

NTAG215 chips also work with the FABA box. They have bigger memory capacity and a few
more features, but more importantly they're mostly as cheap as the NTAG213s.
Since any seller of these chips effectively need to test their functionality
with Nintendo readers for Amiibo clones, their compatibility seems to be significantly higher
(3 out of three cheap Chinese chip types I've tried).

Unfortunately out of the box, these chips start writing user data 5 bytes sooner
than NTAG213, and FABAs need to have the tag number at exact location on
the chip in order to work. There are two possible workarounds for this:

- Instead of writing `02190530012300` onto the tag (for figure id 123), you can write text 5 bytes longer: `abcde02190530012300`. This does work fine, but seems slightly hacky.
- You can use some app that copies tags in binary, without parsing the NDEF records. Duplicate some working figure (e.g. the elephant that came with the box). Once done, the copy can be reprogrammed using e.g. NFC Tools app without using the 5-byte prefix.

Known working app for the second approach is [MiFARE Ultralight Tool](https://play.google.com/store/apps/details?id=com.mtoolstec.mifareultralighttool&hl=en). During writing, it'll report that the first 4 pages cannot be written - that is expected and does not affect the copy.