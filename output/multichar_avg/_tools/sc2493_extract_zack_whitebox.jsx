#target photoshop
app.displayDialogs = DialogModes.NO;

var inputFile = new File("D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/whitebox/SC2493_Zack_whitebox_extract_input.png");
var outputPng = new File("D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/whitebox/SC2493_Zack_whitebox_extracted.png");
var outputPsd = new File("D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/whitebox/SC2493_Zack_whitebox_extracted.psd");
var logFile = new File("D:/NDC_project/output/multichar_avg/SC2493_avg_DannyBathroomWindowWaiver/review/SC2493_Zack_whitebox_extract_log.txt");

try {
    var doc = app.open(inputFile);
    if (doc.activeLayer.isBackgroundLayer) doc.activeLayer.isBackgroundLayer = false;
    executeAction(stringIDToTypeID("autoCutout"), undefined, DialogModes.NO);
    doc.selection.invert();
    doc.selection.clear();
    doc.selection.deselect();
    doc.saveAs(outputPsd, new PhotoshopSaveOptions(), true, Extension.LOWERCASE);
    var png = new PNGSaveOptions();
    png.interlaced = false;
    doc.saveAs(outputPng, png, true, Extension.LOWERCASE);
    doc.close(SaveOptions.DONOTSAVECHANGES);
    logFile.open("w"); logFile.write("PASS\n"); logFile.close();
} catch (e) {
    logFile.open("w"); logFile.write("FAIL: " + e.toString() + "\n"); logFile.close();
    throw e;
}
