
def plt_ois_curve(c1, h1=[0], max_tenor=30, bar_chg=0, sprd=0, name='', fwd_tenor='1y', int_tenor='1y', tail=1,curve_fill=""):
    #### build curves
        c1 = ['SOFR_DC']
    #    h1 = [0,'15-03-2019']
        h1 = [0, -1]
        bar_chg = 1
        sprd = 0
        max_tenor = 30
        tail = 1
        fwd_tenor = '1d'
        int_tenor = '1y'
    #    name = 'Fwd Tenors: '+fwd_tenor
        curve_fill = ''

    n_ccy = len(c1)
    n_chg = len(h1)

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    crv_list = {}

    for k in np.arange(n_ccy):
        c2 = ccy(c1[k], today)
        if c2.ois_trigger == 0:
            crv_list[c1[k]] = [swap_build(c1[k], i) for i in h1]
        else:
            crv_list[c1[k]] = [ois_dc_build(c1[k], b=h1[i]) for i in np.arange(len(h1))]

    crv = flat_lst(list(crv_list.values()))
    h2 = [crv[i].trade_date for i in np.arange(len(crv))]

    if fwd_tenor[-1] == 'd':
        fwd_tenor2 = ql.Days
    elif fwd_tenor[-1] == 'm':
        fwd_tenor2 = ql.Months
    else:
        fwd_tenor2 = ql.Years

    ###### define number of subplots and number of objects !!!!!
    if ((bar_chg == 0) & (sprd == 0)):
        n_plots = 1
        n_obj = {'curve': [n_ccy * n_chg]}
    elif ((bar_chg == 1) & (sprd == 0)):
        if (n_chg < 3):
            n_plots = 2
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_ccy]}

        elif ((n_ccy == 1) & (n_chg > 3)):
            n_plots = 2
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_chg - 1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_chg - 1] * n_ccy}

    elif ((bar_chg == 0) & (sprd == 1)):
        n_plots = 2
        n_obj = {'curve ': [n_ccy * n_chg], 'chg': [n_ccy - 1]}

    else:
        if (n_chg < 3):
            n_plots = 3
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_ccy - 1]}
        elif ((n_ccy == 2) & (n_chg > 3)):
            n_plots = 3
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_chg - 1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_chg - 1] * (n_ccy - 1)}

    ### Define figure
    #mpl.rcParams['axes.facecolor'] = 'white'
    #    plt.rcParams['axes.labelpad'] = 400.00
    grid_h = [2.5] + [1] * (n_plots - 1)
    fig, axs = plt.subplots(n_plots, 1, figsize=(10, 8), gridspec_kw={'height_ratios': grid_h, 'hspace': 0})
    #    len(fig.axes)

    ### Get ALL Data
    rates = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        if crv[i].ois_trigger == 1:
            d2 = crv[i].ref_date
            d3 = d2 + ql.Period(max_tenor, ql.Years)
            #            dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]   #### dates for plotting !!
            #            yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ]
            dates_in2 = ql.MakeSchedule(d2, d3, ql.Period(int_tenor))  #### dates for pricing !!
            yr_axis = [(dates_in2[i] - dates_in2[0]) / 365.25 for i in range(len(dates_in2))]
            rates_c = [100 * crv[i].curve.forwardRate(d, crv[i].cal.advance(d, int(fwd_tenor[0]), fwd_tenor2),
                                                      ql.Actual365Fixed(), ql.Simple).rate() for d in dates_in2]
            rates[c1[int(np.floor(i / len(h1)))]].append(rates_c)


        else:
            yr_axis = np.arange(max_tenor)
            rates_c = []
            j = 0
            while j < max_tenor:
                rates_c.append(Swap_Pricer([[crv[i], j, tail]]).rate[0])
                j += 1
            rates[c1[int(np.floor(i / len(h1)))]].append(rates_c)

    rates_change = dict([(key, []) for key in c1])
    for j in rates.keys():
        k = 1
        while k < n_chg:
            rates_diff = 100 * (np.array(rates[j][0]) - np.array(rates[j][k]))
            rates_change[j].append(rates_diff.tolist())
            k += 1
    bar_dict = rates_change

    if sprd == 1:
        c2 = [c1[0] + ' - ' + c1[i] for i in np.arange(1, n_ccy)]
        spreads = dict([(key, []) for key in c2])
        for i, j in enumerate(spreads.keys()):
            spreads[j] = 100 * (np.array(rates[list(rates.keys())[0]]) - np.array(rates[list(rates.keys())[i + 1]]))

        spreads_change = dict([(key, []) for key in c2])
        for j in spreads.keys():
            k = 1
            while k < n_chg:
                sprd_chg = 1 * (np.array(spreads[j][0]) - np.array(spreads[j][k]))
                spreads_change[j].append(sprd_chg.tolist())
                k += 1
        bar_dict = spreads_change

    ####write in data
    #    r1 = pd.DataFrame(rates)
    #    r2 = pd.DataFrame()
    #    r2['SOFR'] = flat_lst(r1['SOFR_DC'].tolist())
    #    r2['ESTER'] = flat_lst(r1['ESTER_DC'].tolist())
    #    r2['SONIA'] = flat_lst(r1['SONIA_DC'].tolist())
    #    r2.index = [ ql_to_datetime(dates_in2[int(i)]) for i in np.arange(len(dates_in2))]
    #    r2.to_excel("ois_rates.xlsx")

    ### Plot Curve
    yr_axis2 = np.array(yr_axis)
    if ((bar_chg == 0) & (sprd == 0)):
        #        axs.grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs.plot(yr_axis2, rates[i][j], lw=0.5, marker='.', ms=2,
                      label=str(ccy(i, today).curncy) + ': ' + str(h2[j])) for j in
             np.arange(1)]  # prev = label = i+': '+str(h2[j])
            #            axs.text(0.875,-0.15,"Maturity (Yrs)")
            #            axs.text(-0.25,2.5,"Implied Overnight Rate (%)", rotation = 'vertical')
            if len(curve_fill) > 0:
                [axs.fill_between(yr_axis2, rates[i][0], 0,
                                  where=(curve_fill[j][0] < yr_axis2) & (yr_axis2 < curve_fill[j][1]),
                                  fc="C" + str(j + 2), alpha=0.4) for j in np.arange(len(curve_fill))]
        axs.legend(prop={"size": 8}, loc='best')
    else:
        #        axs[0].grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs[0].plot(np.array(yr_axis), rates[i][j], lw=0.5, marker='.', ms=2, label=i + ': ' + str(h2[j])) for j in
             np.arange(1)]
        axs[0].legend(prop={"size": 8}, loc='best')

    # str(ccy('SOFR_DC',today).curncy)   ##### change label from curve to currency

    ### Plot Sprd
    if sprd == 1:
        axs[1].grid(True, 'major', 'both', linestyle=':')
        plt.setp(axs[1], xlim=axs[0].get_xlim())
        for j in spreads.keys():
            axs[1].plot(yr_axis, spreads[j][0], lw=0.5, marker='.', label=str(j))
            axs[1].legend(prop={"size": 8}, loc='best')

        ### Plot Chg
    if sprd == 1:
        start_sub_chg = 2
    else:
        start_sub_chg = 1

    if bar_chg == 1:
        n_sub_chg = len(n_obj['chg'])
        if n_sub_chg == 1:
            axs[start_sub_chg].grid(True, 'major', 'both', linestyle=':')
            plt.setp(axs[start_sub_chg], xlim=axs[0].get_xlim())
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    axs[start_sub_chg].bar(np.array(bar_yr_axis), bar_dict[i][j], width,
                                           label=i + ': ' + str(h1[j + 1]))
                    bar_yr_axis = np.array(bar_yr_axis) + width + 0.1
                axs[start_sub_chg].legend(prop={"size": 8}, loc='best')
        else:
            for j in np.arange(n_sub_chg):
                axs[j + start_sub_chg].grid(True, 'major', 'both', linestyle=':')
                plt.setp(axs[j + start_sub_chg], xlim=axs[0].get_xlim())
                width = 0.15
                bar_yr_axis = yr_axis
                for i in np.arange(len(bar_dict[list(bar_dict.keys())[j]])):
                    axs[j + start_sub_chg].bar(np.array(bar_yr_axis) + 1, bar_dict[list(bar_dict.keys())[j]][i], width,
                                               label=list(bar_dict.keys())[j] + ': ' + str(h1[i + 1]))
                    bar_yr_axis = bar_yr_axis + width + 0.1
                axs[j + start_sub_chg].legend(prop={"size": 8}, loc='best')

#    plt.title(name)
    plt.tight_layout()
    plt.show()
    return fig
