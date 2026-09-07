#target photoshop
app.displayDialogs = DialogModes.NO;

var root = "D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/";
var jobs = [
  ["Zack", "SC2493_Zack_contextual_candidate_v1_raw.png"],
  ["Danny", "SC2493_Danny_contextual_candidate_v1_raw.png"],
  ["Lula", "SC2493_Lula_contextual_candidate_v1_raw.png"],
  ["Mickey", "SC2493_Mickey_contextual_candidate_v1_raw.png"]
];
var log = new File(root + "review/SC2493_ps_extract.txt");
log.open("w");

function extractActor(name, filename) {
  var doc = app.open(new File(root + "candidates/" + filename));
  var backup = doc.activeLayer;
  backup.name = "00_" + name + "_Context_Backup";
  var work = backup.duplicate();
  work.name = "10_" + name + "_SelectSubject_Raw";
  doc.activeLayer = work;
  executeAction(stringIDToTypeID("autoCutout"), undefined, DialogModes.NO);
  doc.selection.invert();
  doc.selection.clear();
  doc.selection.deselect();
  try { work.defringe(1); } catch (e) {}
  backup.visible = false;

  var psd = new File(root + "cutouts/SC2493_" + name + "_cutout_v1.psd");
  doc.saveAs(psd, new PhotoshopSaveOptions(), true, Extension.LOWERCASE);

  var png = new File(root + "cutouts/SC2493_" + name + "_cutout_v1.png");
  var opts = new PNGSaveOptions();
  opts.interlaced = false;
  doc.saveAs(png, opts, true, Extension.LOWERCASE);
  log.writeln("PASS " + name + " " + doc.width.as("px") + "x" + doc.height.as("px"));
  doc.close(SaveOptions.DONOTSAVECHANGES);
}

try {
  for (var i = 0; i < jobs.length; i++) extractActor(jobs[i][0], jobs[i][1]);
  log.writeln("ALL_PASS");
} catch (e) {
  log.writeln("FAIL " + e.toString());
  log.close();
  throw e;
}
log.close();
