using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.DesignScript.Runtime;
using Autodesk.DesignScript.Geometry;
using System.Reflection;
using Autodesk.Revit.DB;
using Revit.Elements;
using RevitServices.Transactions;
using RevitServices.Persistence;

namespace NAMETHISWHATEVERYOUWANT
{
    public class LOAD
    {
        private LOAD()
        {

        }

        public static List<Revit.Elements.Element> FindAllOfCategoryInFile(string SourceFilename, Revit.Elements.Category DynCat)
        {
            Autodesk.Revit.DB.Document doc = DocumentManager.Instance.CurrentDBDocument;
            Autodesk.Revit.UI.UIApplication uiapp = DocumentManager.Instance.CurrentUIApplication;
            //TransactionManager.Instance.EnsureInTransaction(doc);

            Document WallDoc = uiapp.Application.OpenDocumentFile(SourceFilename);

            Autodesk.Revit.DB.Category FoundCat = GetRevitCategory(DynCat);
            
            BuiltInCategory BIcat = (BuiltInCategory)DynCat.Id;

            var Elements = new FilteredElementCollector(WallDoc)
            .OfCategory(BIcat);
            
            List<Revit.Elements.Element> AllElements = new List<Revit.Elements.Element>();

            foreach(Autodesk.Revit.DB.Element TempEle in Elements)
            {
                Revit.Elements.Element WrappedEle = TempEle.ToDSType(false);
                AllElements.Add(WrappedEle);


            }

            return AllElements;
        }

        public static void TransferWallTypeToCurrentDoc(string SourceFilename, Revit.Elements.Element WallElementFromSource)
        {
            Autodesk.Revit.DB.Document doc = DocumentManager.Instance.CurrentDBDocument;
            Autodesk.Revit.UI.UIApplication uiapp = DocumentManager.Instance.CurrentUIApplication;
            //TransactionManager.Instance.EnsureInTransaction(doc);

            

            //Document WallDoc = uiapp.Application.OpenDocumentFile(SourceFilename);

            Autodesk.Revit.DB.Element RevEle = ((Revit.Elements.Element)WallElementFromSource).InternalElement;

            Document WallDoc = RevEle.Document;

            List<ElementId> SourceElements = new List<ElementId>();

            SourceElements.Add(RevEle.Id);
            //SourceElements.Add(RevEle.GetTypeId());

            TransactionManager.Instance.EnsureInTransaction(doc);

            CopyPasteOptions cpOpt = new CopyPasteOptions();

            try
            {
                ElementTransformUtils.CopyElements(WallDoc, SourceElements, doc, Transform.Identity, cpOpt);
            }
            catch (Exception ex)
            {
                
                throw;
            }

            //Close the transaction
            TransactionManager.Instance.TransactionTaskDone();

        }

        

        /// <summary>
        /// Get all objects of a certain category from a linked interface
        /// </summary>
        /// <param name="LinkInstance">Link Instance</param>
        /// <param name="Category">Category</param>
        /// <returns></returns>
        public static Autodesk.Revit.DB.Category GetRevitCategory(Revit.Elements.Category Category)
        {

            System.Reflection.PropertyInfo IntProp = Category.GetType().GetProperty("InternalCategory", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (IntProp == null)
            {
                throw new ArgumentException("No category matching");
            }

            Autodesk.Revit.DB.Category Cat1 = IntProp.GetValue(Category) as Autodesk.Revit.DB.Category;

            if (Cat1 == null)
            {
                throw new ArgumentException("Could not find category");
            }

            return Cat1;

        }

    }
}
