import tkinter as tk
import tkinter.filedialog as fd
import gui.widgets
import event
import webbrowser
import os


class MainWindow:
    def __init__(self, parent_view, tk_root):
        self.parent_view = parent_view
        self.tk_root = tk_root

        tk_root.geometry('800x600')

        self.parent_view.add_observer('title', self.update_title)

        menu_bar = tk.Menu(tk_root)
        tk_root.configure(menu=menu_bar)

        self.file_menu = tk.Menu(menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self._new_file)
        self.file_menu.add_command(label="Open...", command=self._open_file)
        self._save_option_allowed = False
        self.parent_view.add_observer('save_option', self.update_save_option)
        self.file_menu.add_command(label="Save", command=self._save_file)
        self.file_menu.add_command(label="Save As...", command=self._save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=tk_root.quit)
        menu_bar.add_cascade(label="File", menu=self.file_menu)

        menu_bar.add_command(label='Help', command=self._help)

        tk_root.rowconfigure(0, weight=1)
        tk_root.columnconfigure(0, weight=1)
        mainframe = tk.Frame(tk_root)
        mainframe.grid(sticky='nsew')
        mainframe.rowconfigure(1, weight=1)
        mainframe.columnconfigure(0, weight=1)

        top_bar = tk.Frame(mainframe)
        top_bar.grid(column=0, row=0, sticky='nsew')
        top_bar.columnconfigure(0, weight=1)

        # TODO: Add buttons on the tool bar
        '''
        tool_bar = tk.Frame(top_bar)
        tk.Button(tool_bar, text='Test').pack(side=tk.LEFT)
        tool_bar.grid(column=0, row=0, sticky='we')
        '''

        formula_bar = tk.Frame(top_bar)
        formula_bar.grid(column=0, row=1, sticky='we')
        tk.Label(formula_bar, text='Formula:').pack(side=tk.LEFT)

        self.formula_box = tk.Entry(formula_bar)
        self.formula_box.pack(fill=tk.X)
        self.parent_view.add_observer('formula_box', self.update_formula_box)

        self.spreadsheet = gui.widgets.HexCells(mainframe, hex_rows=20, hex_columns=20, select_command=self.select_cell)
        self.spreadsheet.grid(column=0, row=1, sticky='nsew')
        self.parent_view.add_observer('cell_values', self.spreadsheet.set_cell_values)

        self._formula_boxes = [
            self.formula_box,
            self.spreadsheet.hidden_entry
        ]
        vcmd = (self.tk_root.register(self._enter_formula), '%W', '%P')
        for box in self._formula_boxes:
            box.config(vcmd=vcmd)
            box.bind("<FocusIn>", lambda e: e.widget.config(validate='key'))
            box.bind("<FocusOut>", lambda e: e.widget.config(validate='none'))

        self.status_bar = tk.Label(mainframe, relief=tk.GROOVE, anchor=tk.W)
        self.status_bar.grid(column=0, row=2, sticky=(tk.W, tk.E))
        self.parent_view.add_observer('status_bar', self.update_status_bar)

    def update_status_bar(self, text):
        self.status_bar.config(text=text)

    def update_title(self, text):
        self.tk_root.title('HexSheets - ' + text)

    def _enter_formula(self, widget, new_text):
        for box in self._formula_boxes:
            if box != self.tk_root.nametowidget(widget):
                box.delete(0, tk.END)
                box.insert(0, new_text)
        self.parent_view.add_event(event.Event('FormulaChanged', {'formula': new_text}))

        return True

    def update_formula_box(self, text):
        for box in self._formula_boxes:
            validation = box.cget('validate')
            box.config(validate='none')
            box.delete(0, tk.END)
            box.insert(0, text)
            box.config(validate=validation)

    def select_cell(self, address):
        self.parent_view.add_event(event.Event('CellSelected', {'address': address}))

    def _new_file(self):
        self.parent_view.add_event(event.Event('NewFile'))

    def _open_file(self):
        open_file_name = fd.askopenfilename(filetypes=(('HexSheets', '*.hxs'),
                                                       ('All Files', '*.*')))
        self.parent_view.add_event(event.Event('OpenFile', {'filename': open_file_name}))

    def update_save_option(self, option):
        self._save_option_allowed = option

    def _save_file(self):
        if self._save_option_allowed:
            self.parent_view.add_event(event.Event('SaveFile'))
        else:
            self._save_file_as()

    def _save_file_as(self):
        save_file_name = fd.asksaveasfilename(defaultextension='hxs',
                                              filetypes=(('HexSheets', '*.hxs'),
                                                         ('All Files', '*.*')))
        self.parent_view.add_event(event.Event('SaveFileAs', {'filename': save_file_name}))

    def _help(self):
        webbrowser.open_new(os.getcwd() + '/docs/index.html')
