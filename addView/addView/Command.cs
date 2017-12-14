#region Namespaces
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using forms = System.Windows.Forms;
#endregion

namespace addView
{
    [Transaction(TransactionMode.Manual)]
    public class Command : IExternalCommand
    {
        public Result Execute(
          ExternalCommandData commandData,
          ref string message,
          ElementSet elements)
        {
            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Application app = uiapp.Application;
            Document doc = uidoc.Document;
            View activeView = doc.ActiveView;

            using (var form = new Form1())
            {
                //use ShowDialog to show the form as a modal dialog box. 
                form.ShowDialog();

                //if the user hits cancel just drop out of macro
                if (form.DialogResult == forms.DialogResult.Cancel) return Result.Cancelled;

                string sheetNumber = form.TextString.ToString();

                ViewSheet viewSh = null;

                FilteredElementCollector sheets = new FilteredElementCollector(doc).OfClass(typeof(ViewSheet));
                foreach (ViewSheet sht in sheets)
                {
                    if (sht.SheetNumber == sheetNumber)
                        viewSh = sht;
                }


                using (Transaction t = new Transaction(doc))
                {
                    t.Start("Add view to sheet");

                    Viewport newvp = Viewport.Create(doc, viewSh.Id, activeView.Id, new XYZ(1.38, .974, 0));

                    t.Commit();
                }

            }

            return Result.Succeeded;
        }
    }
}
