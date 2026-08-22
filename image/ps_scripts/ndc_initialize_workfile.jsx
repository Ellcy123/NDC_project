#target photoshop

(function () {
    var SCRIPT_NAME = "NDC 工程初始化";
    var BASE_LAYER_NAME = "00_原图";
    var GROUP_NAMES = [
        "10_结构修复",
        "20_内容清理",
        "30_剧情与交互叠层",
        "40_光色统一",
        "90_检查标记"
    ];

    function withoutExtension(fileName) {
        return fileName.replace(/\.[^.]+$/, "");
    }

    function documentNameExists(name) {
        var index;
        for (index = 0; index < app.documents.length; index += 1) {
            if (app.documents[index].name === name) {
                return true;
            }
        }
        return false;
    }

    function makeUniqueDocumentName(baseName) {
        var candidate = baseName + "_NDC_WORK";
        var suffix = 2;

        while (documentNameExists(candidate)) {
            candidate = baseName + "_NDC_WORK_" + suffix;
            suffix += 1;
        }

        return candidate;
    }

    function duplicatePixelLayerToGroup(sourceLayer, group, name, visible, locked) {
        var layer = sourceLayer.duplicate();
        layer.name = name;
        layer.visible = visible;
        layer.move(group, ElementPlacement.INSIDE);
        layer.allLocked = locked;
        return layer;
    }

    function clamp(value, minimum, maximum) {
        return Math.max(minimum, Math.min(maximum, value));
    }

    function copyPixelRegionToGroup(document, sourceLayer, group, name, bounds, visible) {
        var width = document.width.as("px");
        var height = document.height.as("px");
        var left = clamp(bounds[0], 0, width - 1);
        var top = clamp(bounds[1], 0, height - 1);
        var right = clamp(bounds[2], left + 1, width);
        var bottom = clamp(bounds[3], top + 1, height);

        document.activeLayer = sourceLayer;
        document.selection.select([
            [left, top],
            [right, top],
            [right, bottom],
            [left, bottom]
        ]);
        document.selection.copy();
        var layer = document.paste();
        layer.name = name;
        layer.visible = visible;
        layer.move(group, ElementPlacement.INSIDE);
        document.selection.deselect();
        return layer;
    }

    function addHiddenTextLayer(group, name, contents, yPosition) {
        var layer = group.artLayers.add();
        layer.kind = LayerKind.TEXT;
        layer.name = name;
        layer.textItem.contents = contents;
        layer.textItem.position = [24, yPosition];
        layer.textItem.size = 22;
        layer.visible = false;
        return layer;
    }

    function createCurvesAdjustmentLayer(name, points) {
        var makeDescriptor = new ActionDescriptor();
        var makeReference = new ActionReference();
        makeReference.putClass(charIDToTypeID("AdjL"));
        makeDescriptor.putReference(charIDToTypeID("null"), makeReference);

        var adjustmentLayerDescriptor = new ActionDescriptor();
        adjustmentLayerDescriptor.putString(charIDToTypeID("Nm  "), name);

        var curvesDescriptor = new ActionDescriptor();
        var adjustments = new ActionList();
        var compositeCurve = new ActionDescriptor();
        var channelReference = new ActionReference();
        channelReference.putEnumerated(
            charIDToTypeID("Chnl"),
            charIDToTypeID("Chnl"),
            charIDToTypeID("Cmps")
        );
        compositeCurve.putReference(charIDToTypeID("Chnl"), channelReference);

        var curvePoints = new ActionList();
        var index;
        for (index = 0; index < points.length; index += 1) {
            var pointDescriptor = new ActionDescriptor();
            pointDescriptor.putDouble(charIDToTypeID("Hrzn"), points[index][0]);
            pointDescriptor.putDouble(charIDToTypeID("Vrtc"), points[index][1]);
            curvePoints.putObject(charIDToTypeID("Pnt "), pointDescriptor);
        }
        compositeCurve.putList(charIDToTypeID("Crv "), curvePoints);
        adjustments.putObject(charIDToTypeID("CrvA"), compositeCurve);
        curvesDescriptor.putList(charIDToTypeID("Adjs"), adjustments);

        adjustmentLayerDescriptor.putObject(
            charIDToTypeID("Type"),
            charIDToTypeID("Crvs"),
            curvesDescriptor
        );
        makeDescriptor.putObject(
            charIDToTypeID("Usng"),
            charIDToTypeID("AdjL"),
            adjustmentLayerDescriptor
        );
        executeAction(charIDToTypeID("Mk  "), makeDescriptor, DialogModes.NO);
        return app.activeDocument.activeLayer;
    }

    function createBrightnessContrastLayer(name, brightness, contrast) {
        var makeDescriptor = new ActionDescriptor();
        var makeReference = new ActionReference();
        makeReference.putClass(charIDToTypeID("AdjL"));
        makeDescriptor.putReference(charIDToTypeID("null"), makeReference);

        var adjustmentLayerDescriptor = new ActionDescriptor();
        adjustmentLayerDescriptor.putString(charIDToTypeID("Nm  "), name);
        var brightnessContrastDescriptor = new ActionDescriptor();
        brightnessContrastDescriptor.putBoolean(
            stringIDToTypeID("useLegacy"),
            false
        );
        adjustmentLayerDescriptor.putObject(
            charIDToTypeID("Type"),
            charIDToTypeID("BrgC"),
            brightnessContrastDescriptor
        );
        makeDescriptor.putObject(
            charIDToTypeID("Usng"),
            charIDToTypeID("AdjL"),
            adjustmentLayerDescriptor
        );
        executeAction(charIDToTypeID("Mk  "), makeDescriptor, DialogModes.NO);

        var setDescriptor = new ActionDescriptor();
        var setReference = new ActionReference();
        setReference.putEnumerated(
            charIDToTypeID("AdjL"),
            charIDToTypeID("Ordn"),
            charIDToTypeID("Trgt")
        );
        setDescriptor.putReference(charIDToTypeID("null"), setReference);
        var valuesDescriptor = new ActionDescriptor();
        valuesDescriptor.putInteger(charIDToTypeID("Brgh"), brightness);
        valuesDescriptor.putInteger(charIDToTypeID("Cntr"), contrast);
        valuesDescriptor.putBoolean(stringIDToTypeID("useLegacy"), false);
        setDescriptor.putObject(
            charIDToTypeID("T   "),
            charIDToTypeID("BrgC"),
            valuesDescriptor
        );
        executeAction(charIDToTypeID("setd"), setDescriptor, DialogModes.NO);
        return app.activeDocument.activeLayer;
    }

    if (app.documents.length === 0) {
        alert("请先打开一张原始场景图，然后重新运行脚本。", SCRIPT_NAME, true);
        return;
    }

    var sourceDocument = app.activeDocument;
    if (sourceDocument.layers.length !== 1) {
        alert(
            "当前文档不是单层原图。\n\n请关闭测试副本，或重新打开原始 PNG 后再运行。",
            SCRIPT_NAME,
            true
        );
        return;
    }

    var workDocumentName = makeUniqueDocumentName(
        withoutExtension(sourceDocument.name)
    );
    var currentStage = "复制工作文档";
    var originalRulerUnits = app.preferences.rulerUnits;

    try {
        app.preferences.rulerUnits = Units.PIXELS;
        var workDocument = sourceDocument.duplicate(workDocumentName, false);

        currentStage = "创建工作组";
        var groups = {};
        var index;
        for (index = 0; index < GROUP_NAMES.length; index += 1) {
            var group = workDocument.layerSets.add();
            group.name = GROUP_NAMES[index];
            groups[GROUP_NAMES[index]] = group;
        }

        currentStage = "建立结构工作底片";
        var baseLayer = workDocument.layers[workDocument.layers.length - 1];
        if (baseLayer.typename === "ArtLayer" && baseLayer.isBackgroundLayer) {
            baseLayer.isBackgroundLayer = false;
        }
        baseLayer.name = BASE_LAYER_NAME;
        duplicatePixelLayerToGroup(
            baseLayer,
            groups["10_结构修复"],
            "11_结构工作底片_完整原图像素",
            true,
            true
        );
        duplicatePixelLayerToGroup(
            baseLayer,
            groups["10_结构修复"],
            "12_结构修复工作副本_完整原图像素",
            true,
            false
        );
        baseLayer.allLocked = true;

        currentStage = "建立含真实像素的内容清理层";
        duplicatePixelLayerToGroup(
            baseLayer,
            groups["20_内容清理"],
            "21_伪文字与生成噪声清理_完整像素副本",
            true,
            false
        );
        duplicatePixelLayerToGroup(
            baseLayer,
            groups["20_内容清理"],
            "22_边缘与材质修补_完整像素副本",
            true,
            false
        );

        currentStage = "提取 Harrison 调阅车真实像素";
        copyPixelRegionToGroup(
            workDocument,
            baseLayer,
            groups["30_剧情与交互叠层"],
            "31_Harrison调阅车_真实像素区域",
            [1830, 930, 2190, 1390],
            false
        );
        currentStage = "提取中央调阅桌真实像素";
        copyPixelRegionToGroup(
            workDocument,
            baseLayer,
            groups["30_剧情与交互叠层"],
            "32_中央调阅桌_真实像素区域",
            [900, 880, 1940, 1400],
            false
        );
        currentStage = "提取桌面证据区真实像素";
        copyPixelRegionToGroup(
            workDocument,
            baseLayer,
            groups["30_剧情与交互叠层"],
            "33_桌面证据区_真实像素区域_不进底图",
            [1180, 900, 1770, 1130],
            false
        );

        currentStage = "建立实际光色调整层";
        var overallCurve = createCurvesAdjustmentLayer(
            "41_整体明暗曲线_轻提暗部",
            [[0, 0], [32, 37], [128, 131], [220, 221], [255, 255]]
        );
        overallCurve.move(
            groups["40_光色统一"],
            ElementPlacement.INSIDE
        );
        var contrastLayer = createBrightnessContrastLayer(
            "42_整体对比_亮度0_对比4",
            0,
            4
        );
        contrastLayer.move(
            groups["40_光色统一"],
            ElementPlacement.INSIDE
        );
        var finishLayer = createBrightnessContrastLayer(
            "43_最终收束_亮度-1_对比1",
            -1,
            1
        );
        finishLayer.move(
            groups["40_光色统一"],
            ElementPlacement.INSIDE
        );

        currentStage = "建立检查标记层";
        addHiddenTextLayer(
            groups["90_检查标记"],
            "91_修改批注_默认隐藏",
            "NDC 修改批注：机位 / 路线 / 交互区 / 剧情层",
            40
        );
        addHiddenTextLayer(
            groups["90_检查标记"],
            "92_验收顺序_默认隐藏",
            "验收：资产类型 → 机位 → 路线 → 锚点 → 风格 → 瑕疵",
            78
        );

        currentStage = "核验初始化结果";
        if (workDocument.layerSets.length !== GROUP_NAMES.length) {
            throw new Error(
                "工作组数量不正确：预期 " + GROUP_NAMES.length +
                "，实际 " + workDocument.layerSets.length
            );
        }
        if (baseLayer.name !== BASE_LAYER_NAME || !baseLayer.allLocked) {
            throw new Error("00_原图 未正确命名或锁定。");
        }
        if (groups["10_结构修复"].layers.length < 2) {
            throw new Error("结构修复组未建立实际工作层。");
        }
        if (groups["20_内容清理"].layers.length !== 2) {
            throw new Error("内容清理组未建立两个完整像素副本。");
        }
        if (groups["30_剧情与交互叠层"].layers.length !== 3) {
            throw new Error("剧情与交互组未建立三个真实像素区域。");
        }
        if (groups["40_光色统一"].layers.length !== 3) {
            throw new Error("光色统一组未建立三个实际调整层。");
        }

        app.preferences.rulerUnits = originalRulerUnits;
        alert(
            "初始化成功。\n\n" +
            "工作副本：" + workDocument.name + "\n" +
            "已建立完整像素工作副本、三个真实交互区域、" +
            "三个实际调整层与检查标记。\n\n" +
            "原文档未修改；脚本没有保存或导出文件。",
            SCRIPT_NAME
        );
    } catch (error) {
        app.preferences.rulerUnits = originalRulerUnits;
        alert(
            currentStage + "失败。\n\n" +
            "错误：" + error.message + "\n" +
            "行号：" + (error.line || "未知"),
            SCRIPT_NAME,
            true
        );
    }
}());
