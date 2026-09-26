import ctypes,sys
from ctypes import wintypes
from io import StringIO
import tkinter as tk
import tkinter.ttk as ttk

kernel32=ctypes.windll.kernel32

PROCESS_ALL_ACCESS=wintypes.DWORD(0x1FFFFF)
THREAD_ALL_ACCESS=wintypes.DWORD(0x1FFFFF)
TH32CS_SNAPALL=wintypes.DWORD(0x0000001F)

class THREADENTRY32(ctypes.Structure):
    _fields_=[('dwSize',wintypes.DWORD),
              ('cntUsage',wintypes.DWORD),
              ('th32ThreadID',wintypes.DWORD),
              ('th32OwnerProcessID',wintypes.DWORD),
              ('tpBasePri',wintypes.LONG),
              ('tpDeltaPri',wintypes.LONG),
              ('dwFlags',wintypes.DWORD)]

class PROCESSENTRY32(ctypes.Structure):
    _fields_=[('dwSize',wintypes.DWORD),
              ('cntUsage',wintypes.DWORD),
              ('th32ProcessID',wintypes.DWORD),
              ('th32DefaultHeapID',wintypes.PULONG),
              ('th32ModuleID',wintypes.DWORD),
              ('cntThreads',wintypes.DWORD),
              ('th32ParentProcessID',wintypes.DWORD),
              ('pcPriClassBase',wintypes.LONG),
              ('dwFlags',wintypes.DWORD),
              ('szExeFile',wintypes.CHAR*260)]

def get_threads(h_proc):
    thread_list=[]
    thread_entry=THREADENTRY32()
    thread_entry.dwSize=ctypes.sizeof(THREADENTRY32)
    snapshot=kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPALL,wintypes.DWORD(0))
    if kernel32.Thread32First(snapshot,ctypes.byref(thread_entry)):
        while True:
            if thread_entry.th32OwnerProcessID==kernel32.GetProcessId(h_proc):
                thread_list.append(thread_entry.th32ThreadID)
            if not kernel32.Thread32Next(snapshot,ctypes.byref(thread_entry)):
                break
    kernel32.CloseHandle(snapshot)
    return thread_list

def get_processes_by_name(name):
    process_list=[]
    process_entry=PROCESSENTRY32()
    process_entry.dwSize=ctypes.sizeof(PROCESSENTRY32)
    snapshot=kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPALL,wintypes.DWORD(0))
    if kernel32.Process32First(snapshot,ctypes.byref(process_entry)):
        while True:
            if process_entry.szExeFile.decode('utf-8')==name:
                process_list.append(process_entry.th32ProcessID)
            if not kernel32.Process32Next(snapshot,ctypes.byref(process_entry)):
                break
    kernel32.CloseHandle(snapshot)
    return process_list

def get_processes_name_by_pid(pid):
    process_entry=PROCESSENTRY32()
    process_entry.dwSize=ctypes.sizeof(PROCESSENTRY32)
    snapshot=kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPALL,wintypes.DWORD(0))
    if kernel32.Process32First(snapshot,ctypes.byref(process_entry)):
        while True:
            if process_entry.th32ProcessID==pid:
                kernel32.CloseHandle(snapshot)
                return process_entry.szExeFile.decode('utf-8')
            if not kernel32.Process32Next(snapshot,ctypes.byref(process_entry)):
                break
    kernel32.CloseHandle(snapshot)
    return None

def proc(cmd:str,mode:str,pid=0,name=None,outstream=sys.stdout):
    if mode == 'pid':
        if (name:=get_processes_name_by_pid(pid)) is not None:
            print(f'Process name: {name}', file=outstream)
            h_process=kernel32.OpenProcess(PROCESS_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(pid))
            threads=get_threads(h_process)
            if cmd == 'suspend':
                for thread_id in threads:
                    h_thread=kernel32.OpenThread(THREAD_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(thread_id))
                    kernel32.SuspendThread(h_thread)
                    kernel32.CloseHandle(h_thread)
            elif cmd == 'resume':
                for thread_id in threads:
                    h_thread=kernel32.OpenThread(THREAD_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(thread_id))
                    kernel32.ResumeThread(h_thread)
                    kernel32.CloseHandle(h_thread)
        else:
            print('Process not found.', file=outstream)
    elif mode == 'name':
        pids=get_processes_by_name(name)
        if len(pids) == 0:
            print('Process not found.', file=outstream)
        else:
            for pid in pids:
                print(f'Process PID: {pid}', file=outstream)
                h_process=kernel32.OpenProcess(PROCESS_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(pid))
                threads=get_threads(h_process)
                if cmd == 'suspend':
                    for thread_id in threads:
                        h_thread=kernel32.OpenThread(THREAD_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(thread_id))
                        kernel32.SuspendThread(h_thread)
                        kernel32.CloseHandle(h_thread)
                elif cmd == 'resume':
                    for thread_id in threads:
                        h_thread=kernel32.OpenThread(THREAD_ALL_ACCESS,wintypes.BOOL(False),wintypes.DWORD(thread_id))
                        kernel32.ResumeThread(h_thread)
                        kernel32.CloseHandle(h_thread)

def tui_main():
    cmd=input('What do you want to do with the process?(suspend or resume)')
    mode=input('What mode do you want to use?(pid or name)')
    pid=int(input('Enter the PID of the process:')) if mode == 'pid' else 0
    name=input('Enter the name of the process:') if mode == 'name' else None
    proc(cmd,mode,pid,name)

def gui_main():
    root=tk.Tk()
    root.title('ThreadTool')
    root.geometry('800x600+200+100')

    ttk.Label(root,text='What do you want to do with the process?').place(relx=0.05,rely=0.05)
    cmd_var=tk.StringVar()
    ttk.Radiobutton(root,text='suspend',variable=cmd_var,value='suspend').place(relx=0.075,rely=0.1)
    ttk.Radiobutton(root,text='resume',variable=cmd_var,value='resume').place(relx=0.075,rely=0.15)

    ttk.Label(root,text='What mode do you want to use?').place(relx=0.05,rely=0.25)
    mode_var=tk.StringVar()
    ttk.Radiobutton(root,text='pid',variable=mode_var,value='pid').place(relx=0.075,rely=0.3)
    ttk.Radiobutton(root,text='name',variable=mode_var,value='name').place(relx=0.075,rely=0.35)

    name_var=tk.StringVar()
    name_frame=ttk.Frame(root,width=400,height=300)
    ttk.Label(name_frame,text='Enter the name of the process:').place(relx=0.1,rely=0)
    ttk.Entry(name_frame,textvariable=name_var).place(relx=0.15,rely=0.075)

    pid_var=tk.IntVar()
    pid_frame=ttk.Frame(root,width=400,height=300)
    ttk.Label(pid_frame,text='Enter the PID of the process:').place(relx=0.1,rely=0)
    ttk.Entry(pid_frame,textvariable=pid_var).place(relx=0.15,rely=0.075)

    def update_question():
        nonlocal name_frame,pid_frame
        if mode_var.get() == 'pid':
            name_frame.place_forget()
            pid_frame.place(relx=0,rely=0.45)
        else:
            pid_frame.place_forget()
            name_frame.place(relx=0,rely=0.45)
        root.after(100,update_question)

    update_question()

    outstream=StringIO()
    text_widget=tk.Text(root,state='disabled')
    text_widget.place(relx=0.5,rely=0.05,relwidth=0.45,relheight=0.7)

    def update_output():
        nonlocal outstream,text_widget
        text_widget.config(state='normal')
        text_widget.delete('1.0','end')
        text_widget.insert('1.0',outstream.getvalue())
        text_widget.config(state='disabled')
        root.after(100,update_output)

    update_output()

    def start():
        pid=pid_var.get() if mode_var.get() == 'pid' else 0
        name=name_var.get() if mode_var.get() == 'name' else None
        proc(cmd_var.get(),mode_var.get(),pid,name,outstream)
    ttk.Button(root,text='start',command=start).place(relx=0.8,rely=0.8)

    root.mainloop()

if len(sys.argv) == 1:
    #if input('tui or gui?') == 'tui':
    #    tui_main()
    #else:
    gui_main()
elif len(sys.argv) == 4:
    cmd=sys.argv[1]
    mode=sys.argv[2]
    pid=int(sys.argv[3]) if mode == 'pid' else 0
    name=sys.argv[3] if mode == 'name' else None
    proc(cmd,mode,pid,name)
else:
    print('Invalid arguments. Usage: python threadtool.py [suspend/resume] [pid/name] [process_id/process_name]')
#print(kernel32.GetLastError())