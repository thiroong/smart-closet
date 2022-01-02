import matplotlib.pyplot as plt
import numpy as np
import clothOps

def circle_graph():
    cnt_categorise = clothOps.count_by_category()
    count = []
    labels = []
    explode = []
    
    for key, val in cnt_categorise.items():
        if (val != 0):
            labels.append(key)
            count.append(val)
            explode.append(0.05)
    
    # 부채꼴이 파이 차트의 중심에서 벗어나는 정도
    wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
    # 부채꼴 영역의 스타일을 설정

    plt.pie(count, labels=labels, autopct = '%.1f%%', startangle=90, counterclock=False, explode=explode, wedgeprops=wedgeprops)
    plt.show()

# circle_graph()

def stick_graph():
    cnt_categorise = clothOps.count_by_category_to_date()
    count = []
    labels = []
    arrange = 0
    
    for key, val in cnt_categorise.items():
        if (val != 0):
            labels.append(key)
            count.append(val)
            arrange += 1
    
    x = np.arange(arrange)
    plt.bar(x, count)
    plt.xticks(x, labels)
    plt.show()

# stick_graph()
    