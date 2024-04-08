import polars as pl
import pandas as pd
import timeit

def bond_fut_yield(fut_ticker, fut_px):
    con = pdblp.BCon(debug=False, port=8194, timeout=50000)
    con.start()
#    fut_ticker = fut[:4]
#    fut_px = df2['strikes'].tolist()

    # bond future
    bond_fut_dets = con.ref(fut_ticker + ' Comdty', ['FUT_CTD_ISIN', 'FUT_DLV_DT_LAST', 'FUT_CNVS_FACTOR', 'CRNCY', 'PX_LAST'])['value']
    fut_last = bond_fut_dets.pop(bond_fut_dets.index[-1])
    fwd_px = fut_last * bond_fut_dets[2]
    strike_px = np.array(fut_px) * bond_fut_dets[2]

    # ctd
    fwd_yield = con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'], ovrds=[('PX_BID', fwd_px), (('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0]

    # yield retriever for strikes
    def get_strike_yield(strike):
        bond_yield = con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'], ovrds=[('PX_BID', strike), ('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0))])['value'][0]
        return bond_yield

    # concurrent api calls
    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        yields = executor.map(get_strike_yield, strike_px)
    strike_yield = list(yields)

    # dataframe builder
    bond_fut_yield_tab = pd.DataFrame()
    bond_fut_yield_tab['Fut'] = np.repeat(fut_ticker, len(fut_px))
    bond_fut_yield_tab['Fut'] = np.repeat(fut_ticker, len(fut_px))
    if bond_fut_dets[3] == 'USD':
        bond_fut_yield_tab['Fut_Px'] = np.repeat(px_dec_to_frac(fut_last), len(fut_px))
    else:
        bond_fut_yield_tab['Fut_Px'] = np.repeat(fut_last, len(fut_px))

    bond_fut_yield_tab['Fut_Yield'] = np.repeat(fwd_yield, len(fut_px))
    bond_fut_yield_tab['K_Yield'] = np.array(sorted((strike_yield), reverse=True))
    bond_fut_yield_tab['K_'] = np.array(sorted(fut_px, reverse=False))
    bond_fut_yield_tab['K_Dist'] = 100 * np.array(sorted(strike_yield, reverse=True) - fwd_yield)

    return bond_fut_yield_tab


%%timeit -n1 -r5
df3 = bond_fut_yield(fut[:4], np.unique(df2['strikes']).tolist() )


%%timeit -n1 -r5
df4 = bond_fut_yield3(fut[:4], np.unique(df2['strikes']).tolist() ).select(pl.col("K_Dist")).collect()



def bond_fut_yield3(fut_ticker, fut_px):
    con = pdblp.BCon(debug=False, port=8194, timeout=50000)
    con.start()
#    fut_ticker = fut[:4]
#    fut_px = df2['strikes'].tolist()

    # bond future
    bond_fut_dets = con.ref(fut_ticker + ' Comdty', ['FUT_CTD_ISIN', 'FUT_DLV_DT_LAST', 'FUT_CNVS_FACTOR', 'CRNCY', 'PX_LAST'])['value']
    fut_last = bond_fut_dets.pop(bond_fut_dets.index[-1])
    fwd_px = fut_last * bond_fut_dets[2]
    strike_px = np.array(fut_px) * bond_fut_dets[2]

    # ctd
    fwd_yield = con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'], ovrds=[('PX_BID', fwd_px), (('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0]

    # yield retriever for strikes
    def get_strike_yield(strike):
        bond_yield = con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'], ovrds=[('PX_BID', strike), ('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0))])['value'][0]
        return bond_yield

    # dataframe builder
    bond_fut_yield_tab = pl.LazyFrame({'Fut': list(np.repeat(fut_ticker, len(fut_px))),
                                       'Fut_Px':  list(np.repeat(px_dec_to_frac(fut_last), len(fut_px))),
                                       'Fut_Yield': list(np.repeat(fwd_yield, len(fut_px))),
                                       'K_' : list(strike_px)})

    output = bond_fut_yield_tab.with_columns(pl.col("K_").map_elements(get_strike_yield).alias('K_Yield')).with_columns(K_Dist = 100*(pl.col('K_Yield')-pl.col('Fut_Yield')) )

    return output




df_k_polar = pl.DataFrame({'k':list(strike_px)})
df_k_polar.with_columns((pl.struct(["k"])).map_batches(lambda x: get_strike_yield(x.struct.field("k"))).alias('yield'))
df_k_polar.group_by("k", maintain_order=True).agg(pl.col("k").map_elements(get_strike_yield).alias("kd"))



df_k_polar.with_columns((pl.col(["k"])).map_elements(get_strike_yield).alias('yield'))

%%timeit -n1 -r5
df_k_polar.with_columns((pl.col(["k"])).map_elements(lambda x: get_strike_yield(x)).alias('yield'))

%%timeit -n1 -r5
df_k_polar.with_columns(
    (pl.col(["k"])).map_elements(lambda x: con.ref(bond_fut_dets[0]+' Govt', ['YLD_YTM_BID'], ovrds=[('PX_BID', x), (('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0]).alias('yield'))



%%timeit -n1 -r5
[con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'],ovrds=[('PX_BID', kpx), ('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0))])['value'][0] for kpx in strike_px]

con.ref(bond_fut_dets[0] + ' Govt', ['YLD_YTM_BID'],ovrds=[('PX_BID', [100, 99]), ('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0))])['value']


get_strike_yield(105.0*bond_fut_dets[2])
get_strike_yield(106*bond_fut_dets[2])