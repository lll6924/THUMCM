from dataset import *
from match import *
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

NUM=5

def analyze_serve(matches,name):
    serves=[]
    for m in matches:
        for s in m._sets:
            for p in s._points:
                bat=p._bats[0]
                if p._server==name:
                    if bat._fall is None:
                        strategy=bat._method
                    else:
                        strategy=bat._method+'-'+bat._fall
                    found=False
                    for s in serves:
                        if s["strategy"]==strategy:
                            s["total"]+=1
                            if(p._winner==name):
                                s["win"]+=1
                            found=True
                            break
                    if found==False:
                        serves.append({"strategy":strategy,"total":1,"win":int(p._winner==name)})
    serves=pd.DataFrame(serves).sort_values("total",ascending=False)
    plt.margins(x=0.1)
    sns.set_color_codes("pastel")

    sns.barplot(x="total", y="strategy", data=serves,
                label="Total", color="b")

    sns.set_color_codes("muted")
    sns.barplot(x="win", y="strategy", data=serves,
                label="Win", color="b")
    plt.legend(loc="lower right")
    plt.xlabel("Win/Total")
    plt.title("the serve of "+name)
    for i,(index,row) in zip(range(len(serves)),serves.iterrows()):
        #print(row.strategy,row.total,row.win,str(row.win/row.total),index)
        plt.text(row.total,i,str(round(row.win/row.total,3)),color="black",ha='left')
    #plt.show()
    if not os.path.exists("img"):
        os.mkdir("img")
    plt.savefig(os.path.join("img","serve_"+name+".png"))
    plt.clf()

def analyze_receive(matches,name):
    serves=[]
    for m in matches:
        for s in m._sets:
            for p in s._points:
                bat=p._bats[0]
                if p._server==another(name):
                    if bat._fall is None:
                        strategy=bat._method
                    else:
                        strategy=bat._method+'-'+bat._fall
                    if (name=="fan" and strategy in["a-B1","a-C1","a-A1","a-C2","a-B2"]) or \
                        name=="ma" and strategy in["b-A1","b-B1","c-B1","c-C1","a-B1"]:
                        if(len(p._bats)<2):
                            continue
                        anti_bat=p._bats[1]
                        if anti_bat._fall is None:
                            anti_strategy = anti_bat._method
                        else:
                            anti_strategy = anti_bat._method + '-' + anti_bat._fall
                        found=False
                        for s in serves:
                            if s["strategy"]==strategy and s["antistrategy"]==anti_strategy:
                                s["total"]+=1
                                if(p._winner==name):
                                    s["win"]+=1
                                found=True
                                break
                        if found==False:
                            serves.append({"strategy":strategy,"antistrategy":anti_strategy,"total":1,"win":int(p._winner==name)})
    serves=pd.DataFrame(serves)
    serves=serves[serves.total>4]
    ax=sns.barplot(x="strategy", y="total", hue="antistrategy", data=serves,palette="pastel")
    h, l = ax.get_legend_handles_labels()
    sns.barplot(x="strategy", y="win",hue="antistrategy", data=serves,palette="muted",ax=ax)
    plt.xlabel("The serve of "+another(name))
    plt.title("The receive of "+name)
    if not os.path.exists("img"):
        os.mkdir("img")
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join("img","receive_"+name+".png"))
    plt.clf()

def analyze():
    matches=[]
    for i in range(NUM):
        d=getdata(i)
        matches.append(d)
    analyze_serve(matches,'ma')
    analyze_serve(matches,'fan')
    analyze_receive(matches,'ma')
    analyze_receive(matches,'fan')

if __name__=="__main__":
    analyze()