#!/usr/bin/env python
# Version 1.0
# License: GPL v3
# Author: ZiLin Chen
# E-Mail: chenzilin115@gmail.com
# Copyright 2015 ZiLin Chen
# GIMP plugin to export layers as QML

from gimpfu import *
import os

imagepath = ""

gettext.install("gimp20-python", gimp.locale_directory, unicode = True)

def format_color(color) :
    return "Qt.rgba(%i, %i, %i, %i)" % (color[0]/255.0, 
    color[1]/255.0, 
    color[2]/255.0,
    color[3]/255.0)

def fix_name(name) :
    fixedname = name
    fixedname = fixedname.replace(' ', '_')
    fixedname = fixedname.replace('#', '__')
    fixedname = fixedname.replace('!', '___')
    fixedname = fixedname.replace('/', '_')
    fixedname = fixedname.replace(':', '_')
    return fixedname

def dump_common_properties(layer, qmlx, qmly, layername, f) :
    f.write('        id: ' + layername +'\n')
    px = int(layer.offsets[0]) - int(qmlx)
    f.write('        x: %s' % px + '\n')
    py = int(layer.offsets[1]) - int(qmly)
    f.write('        y: %s' % py + '\n')
    opacity = layer.opacity / 100.0
    f.write('        opacity: %s' % opacity +'\n')

def dump_text_element(layer, qmlx, qmly, layername, f):
    f.write('    Text {\n')
    dump_common_properties(layer, qmlx, qmly, layername, f)
    f.write('        text: \'%s\''   %  pdb.gimp_text_layer_get_text(layer) + '\n')
    color =  pdb.gimp_text_layer_get_color(layer)
    f.write('        color: ' +  format_color(color) + '\n')
    f.write('        font.pixelSize: %i '   %  pdb.gimp_text_layer_get_font_size(layer)[0] + '\n')
    f.write('    }\n')

def dump_image_element(layer, qmlx, qmly, layername, f, image, imagepath):
    opacity = layer.opacity / 100.0
    name = imagepath + '/' + layername + ".png"
    fullpath = name

    # write out the element
    f.write('    Image {\n')
    # dump common properties
    dump_common_properties(layer, qmlx, qmly, layername, f)

    # store the layer as a .png
    pdb.file_png_save(image, layer, fullpath, name, 0, 9, 1, 1, 1, 1, 1)
    f.write('        source: \"' + "qrc:"+ imagepath + "/" + layername + '.png\"\n')
    f.write('    }\n')

def solve_layer(layer, qmlx, qmly, f, copyImage, flatten, childimagepath):
    layername = fix_name(layer.name)
    if pdb.gimp_drawable_is_text_layer(layer) and not flatten :
        dump_text_element(layer, qmlx, qmly, layername, f)
    else :
        dump_image_element(layer, qmlx, qmly, layername, f, copyImage, childimagepath)

def get_layers(layers, qmlx, qmly, f, copyImage, flatten, only_visible, imagepath):
    i = len(layers) - 1
    while i >= 0:
        layer = layers[i]
        if pdb.gimp_item_is_group(layer):
            if layer.visible:
                # create a subfolder for the image content
                childimagepath = imagepath + '/' + fix_name(layer.name);
                if not os.path.isdir(childimagepath):
                    os.mkdir(childimagepath)
                f.write('    // module ' + fix_name(layer.name) +'\n')
                get_layers(layer.children, qmlx, qmly, f, copyImage, flatten, only_visible, childimagepath)
                f.write('\n')
        else:
            if only_visible:
                if layer.visible:
                    solve_layer(layer, qmlx, qmly, f, copyImage, flatten, imagepath)
            else:
                solve_layer(layer, qmlx, qmly, f, copyImage, flatten, imagepath)
        i = i - 1

def export_qml(image, qmlname, qmlx, qmly, qmlw, qmlh, path, only_visible, flatten):
    qmlfilename = os.path.join(path, qmlname + '.qml')

    # create a qml file to write image content
    f = open(qmlfilename, 'w')
    f.write('import QtQuick 2.4\n\n')
    f.write('Item {\n')
    tmpqmlname = qmlname[0].lower() + qmlname[1:]
    qmlname = tmpqmlname
    f.write('    id: ' + qmlname +'\n')
    f.write('    x: ' + qmlx +'\n')
    f.write('    y: ' + qmly +'\n')
    f.write('    width: ' + qmlw + '\n')
    f.write('    height: ' + qmlh + '\n\n')

    # create a folder for the image content
    imagepath = os.path.join(path, qmlname)
    if not os.path.isdir(imagepath):
        os.mkdir(imagepath)

    get_layers(image.layers, qmlx, qmly, f, image, flatten, only_visible, imagepath)

    f.write('\n    states: [\n')
    f.write('        State {\n')
    f.write('            name: \"\"\n')
    f.write('        },\n')
    f.write('        State {\n')
    f.write('            name: \"show\"\n')
    f.write('        }\n')
    f.write('    ]\n')
    f.write('\n    transitions: [\n')
    f.write('        Transition {\n')
    f.write('            from: \"\"\n')
    f.write('            to: \"show\"\n')
    f.write('            SequentialAnimation {\n')
    f.write('            }\n')
    f.write('        },\n')
    f.write('        Transition {\n')
    f.write('            from: \"show\"\n')
    f.write('            to: \"\"\n')
    f.write('            SequentialAnimation {\n')
    f.write('            }\n')
    f.write('        }\n')
    f.write('    ]\n')

    f.write('}\n')
    f.close()

register(
    proc_name = ("python-fu-export-qml"),
    blurb = ("Export layers to a QML document"),
    help = ("Export layers as a QML document."),
    author = ("ZiLin Chen"),
    copyright = ("ZiLin Chen"),
    date = ("2015"),
    label = ("Export to _QML"),
    imagetypes=("*"),
    params=[
        (PF_IMAGE, "image", "Image", None),
        (PF_STRING, "qmlname", "QML Element Id:", "MyElement"),
        (PF_STRING, "qmlx", "QML Element X:", "0"),
        (PF_STRING, "qmly", "QML Element Y:", "0"),
        (PF_STRING, "qmlw", "QML Element Width:", "0"),
        (PF_STRING, "qmlh", "QML Element Height:", "0"),
        (PF_DIRNAME, "path", "Save QML to this Directory", os.getcwd()),
        (PF_BOOL, "only_visible", "Only Export Visible Image:", 1),
        (PF_BOOL, "flatten", "Convert text to image:", 0),
    ],
    results=[],
    function=(export_qml),
    menu=("<Image>/File"),
    domain=("gimp20-python", 
    gimp.locale_directory)
)

main()
