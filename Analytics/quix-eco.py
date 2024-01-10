class Eco(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        label_tab = tk.Label(self, text="Eco", font=LARGE_FONT, bg="light grey", fg='blue')
        label_tab.grid(row=0, column=0, columnspan=5, sticky='W')

        m = tk.StringVar()
        m.set('GDP CPI PCE Core-PCE UNEMP FISC')
        ticker_lstbox = tk.Listbox(self, listvariable=m, selectmode='multiple', width=14, height=10,
                                   exportselection=False)
        ticker_lstbox.grid(column=0, row=2, rowspan=15, columnspan=1, sticky='W', padx=5)

        m2 = tk.StringVar()
        m2.set('US EU GB DE FR IT ES CA AU NZ SE NO CH JP KR CN')
        country_lstbox = tk.Listbox(self, listvariable=m2, selectmode='multiple', width=14, height=10,
                                    exportselection=False)
        country_lstbox.grid(column=1, row=2, rowspan=20, columnspan=1, sticky='W', padx=5)

        m3 = tk.StringVar()
        m3.set('2022 2023 2024 2025 2026')
        yr_lstbox = tk.Listbox(self, listvariable=m3, selectmode='multiple', width=14, height=10, exportselection=False)
        yr_lstbox.grid(column=2, row=2, rowspan=15, columnspan=1, sticky='W', padx=5)

        m4 = tk.StringVar()
        m4.set('BAR BOA BNP CE CIT CAG CSU DNS FTC GS HSB IG JPM MS NTX NS NDA PMA UBS WF SCB')
        contrib_lstbox = tk.Listbox(self, listvariable=m4, selectmode='multiple', width=14, height=10,
                                    exportselection=False)
        contrib_lstbox.grid(column=3, row=2, rowspan=20, columnspan=1, sticky='W', padx=5)

        m5 = tk.StringVar()
        m5.set('FED ECB BOE OEC IMF WB EU EC OBR IST DBK ISE BOC RBA RIK NOR NPC ')
        offi_lstbox = tk.Listbox(self, listvariable=m5, selectmode='multiple', width=14, height=10,
                                 exportselection=False)
        offi_lstbox.grid(column=4, row=2, rowspan=15, columnspan=1, sticky='W', padx=5)

        def PlotButton1():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]

            print(a1, a2, a3, a4, a5)

            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1=a4[0], off=a5[0])

            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=30, column=5, columnspan=7, sticky='nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=32, column=5)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button1 = ttk.Button(self, text="Plot1", width=10, command=PlotButton1)
        plot_button1.grid(column=0, row=1, rowspan=1, columnspan=1, sticky=tk.W, padx=5)

        def PlotButton2():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]

            print(a1, a2, a3, a4, a5)

            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1=a4[0], off=a5[0])

            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=30, column=13, columnspan=7, sticky='nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=32, column=13)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button2 = ttk.Button(self, text="Plot2", width=10, command=PlotButton2)
        plot_button2.grid(column=1, row=1, rowspan=1, columnspan=1, sticky=tk.W, padx=5)

        def PlotButton3():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]

            print(a1, a2, a3, a4, a5)

            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1=a4[0], off=a5[0])

            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=45, column=5, columnspan=7, sticky='nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=46, column=5)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button3 = ttk.Button(self, text="Plot3", width=10, command=PlotButton3)
        plot_button3.grid(column=2, row=1, rowspan=1, columnspan=1, sticky=tk.W, padx=5)

        def PlotButton4():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]

            print(a1, a2, a3, a4, a5)

            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1=a4[0], off=a5[0])

            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=45, column=13, columnspan=7, sticky='nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=46, column=13)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button4 = ttk.Button(self, text="Plot4", width=10, command=PlotButton4)
        plot_button4.grid(column=3, row=1, rowspan=1, columnspan=1, sticky=tk.W, padx=5)
