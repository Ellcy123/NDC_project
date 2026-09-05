#target photoshop
app.displayDialogs = DialogModes.NO;
var root = "D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/cutouts/";
var jobs = [["Lula", 330, 380], ["Mickey", 185, 325]];
var log = new File("D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/review/SC2493_ps_reextract_window.txt");
log.open("w");
function run(name) {
  var doc = app.open(new File(root + "SC2493_" + name + "_tight_extract_input.png"));
  if (doc.activeLayer.isBackgroundLayer) doc.activeLayer.isBackgroundLayer = false;
  executeAction(stringIDToTypeID("autoCutout"), undefined, DialogModes.NO);
  doc.selection.invert();
  doc.selection.clear();
  doc.selection.deselect();
  try { doc.activeLayer.defringe(1); } catch (e) {}
  var png = new PNGSaveOptions(); png.interlaced = false;
  doc.saveAs(new File(root + "SC2493_" + name + "_tight_cutout.png"), png, true, Extension.LOWERCASE);
  log.writeln("PASS " + name);
  doc.close(SaveOptions.DONOTSAVECHANGES);
}
try { run("Lula"); run("Mickey"); log.writeln("ALL_PASS"); }
catch (e) { log.writeln("FAIL " + e.toString()); log.close(); throw e; }
log.close();
