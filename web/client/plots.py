import json
import plotly as py
import plotly.express as px
import pandas as pd

def prob_graph(labels, pred):
    '''
        [argument]
            labels      : [list] 옷의 종류 리스트
            pred        : [list] 옷의 종류별 확률 값
        [action]
                        : 옷의 분류의 확률그래프를 그리기 위해
                        plotly를 활용하여 그래프를 그리는 부분
        [return]
                    : [json] plotly graph json
    '''
    data = pd.DataFrame(pred, labels, columns=["probability"])
    fig = px.bar(data_frame=data, x=data.index, y="probability",
                 color="probability", title="옷 분류별 확률")
    graphJSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)
    return graphJSON