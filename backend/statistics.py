import matplotlib.pyplot as plt
import numpy as np

# 원형 그래프
count = [9,5,3,1]
labels = ['knit', 'shirt','shortsleeve','longsleeve']
explode = [0.05, 0.05, 0.05, 0.05]
# 부채꼴이 파이 차트의 중심에서 벗어나는 정도
wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
# 부채꼴 영역의 스타일을 설정

plt.clear
plt.pie(count, labels=labels, autopct = '%.1f%%', startangle=90, counterclock=False, explode=explode, wedgeprops=wedgeprops)
plt.show()


# 막대그래프
x = np.arange(4)
clothes = ['knit_A', 'shirt_B', 'shortsleeve_C', 'longsleeve_D']
values = [8, 2, 4, 1]

plt.clear()
plt.bar(x, values)
plt.xticks(x, clothes)
plt.show()