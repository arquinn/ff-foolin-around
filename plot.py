from pandas import DataFrame
from adjustText import adjust_text

import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("fivethirtyeight")


def ew_v_w(df):
    agg = df.rename(columns = {"Win":"Wins", "Exp Win": "Exp Wins"})\
            .sort_values(by="Exp Wins")

    print("get plot")
    ax = agg.plot(kind="scatter", x="Exp Wins", y="Wins", title="Exp Wins vs. Wins")

    ann = []
    for x,y,val in zip(agg['Exp Wins'], agg['Wins'], agg.index.to_series()):
        ann.append(ax.text(x,y,val))

    #identiy line:
    maxW = agg['Wins'].max()
    ident = range(maxW+1)
    maxWs = [maxW for i in ident]

    #ax.plot(ident, ident, color='black)
    ax.fill_between(ident, ident, color='red', alpha=0.3)
    ax.fill_between(ident, ident, maxWs, color='blue', alpha=0.3)

    ax.set_xlim(0, maxW)
    ax.set_ylim(-.25, maxW + .25)
    ax.text(.125, maxW - .25, "Lucky", color='blue')
    ax.text(maxW - .5, .25,"Unlucky", color='red')

    adjust_text(ann, agg['Exp Wins'], agg['Wins'])

    plt.show()
