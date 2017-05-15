#Sometimes a pick selection is better
#Based on a node from Dimitar Venkov
import clr

clr.AddReference("RevitAPIUI")
from  Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
doc = DocumentManager.Instance.CurrentDBDocument
uidoc=DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)

sel1 = uidoc.Selection
ot1 = Selection.ObjectType.Element
el_ref = sel1.PickObjects(ot1, "Select model elements")
typelist = list()
idlist = list()
for i in el_ref:

	try:
		typelist.append(doc.GetElement(i.ElementId))
	except:
		typelist.apped(list())


OUT = typelist
