This is a simple file exporter from GIMP to QML.

This means you can export QML scenes directly from GIMP.
Indirectly this also means you can export Phothoshop .psd files to qml.

Saving each layer as an image component with opacity preserved Images are dumped into
an images subdirectory Text layers are exported as QML Text elements with color, font size and opacity preserved. 

INSTALLATION
To use this plugin, make sure you have a recent version of GIMP 2.8(or newer) installed.

- Copy the file qmlexporter.py to ~/.gimp-<version>/plug-ins
- Run chmod u+rx on the file to make sure it is executable
- Run or restart gimp

The exporter should now show up at the bottom of the File menu.
When you run it, it will ask for the following:
- the element id 
- the root element position of x
- the root element position of y
- the root element width
- the root element height
- the directory
- whether only export visible image
- whether convert text to image
