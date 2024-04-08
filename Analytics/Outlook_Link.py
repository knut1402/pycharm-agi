import os
import pythoncom
import win32com.client
#pythoncom.CoInitialize()
from matplotlib import cm
from zipfile import ZipFile
from tabulate import tabulate

#warnings.simplefilter(action='ignore', category=FutureWarning)
#pd.options.display.float_format = "{:,.2f}".format
#pd.options.mode.chained_assignment = None
#os.getcwd()

file_path = os.path.dirname(os.path.abspath('C:\\Users\\A00007579\\PycharmProjects\\pythonProject\\Analytics'))
path = os.path.join(file_path, 'temporary')
outlook = win32com.client.Dispatch("Outlook.Application",pythoncom.CoInitialize())
namespace = outlook.GetNamespace("MAPI")
inbox = namespace.GetDefaultFolder(6)
folder = inbox.Folders.Item("Citi-Batch")
#folder = folder_header.Folders.Item("Positions")
messages = folder.Items



def save_attachments() -> None:
    file_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(file_path, 'temporary')
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)
    folder_header = inbox.Folders.Item("Macro Unconstrained").Folders.Item("Operations")
    folder = folder_header.Folders.Item("Positions")
    messages = folder.Items

for message in folder.Items:
    print(message.Body)
    # print(message)


#    for attachment in message.Attachments:
#        attachment.SaveAsFile(os.path.join(path, str(attachment.FileName)))
#    if message.UnRead:
#        message.UnRead = False
#    message.Move(folder.Folders.Item("Extracted"))




xl=win32com.client.Dispatch("Excel.Application",pythoncom.CoInitialize())