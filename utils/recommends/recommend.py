from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import KNeighborsClassifier
from typing import List, Dict
import pickle


class Recommend:
    def recommend_similar_knn(self, current_goods: Dict, data: List) -> List[Dict]:
        """
        通过KNN算法对商品进行推荐

        :param current_goods: 当前商品
        :param data: 商品集合
        :return: 推荐商品集合
        """
        # 数据预处理：将每个商品的type转化为二进制向量(binary vector)
        mlb = MultiLabelBinarizer()
        X = mlb.fit_transform([d['categories'] for d in data])
        # 训练KNN分类器
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X, [d['uid'] for d in data])

        # 将KNN模型保存到磁盘
        # with open('knn_model.pkl', 'wb') as file:
        #     pickle.dump(knn, file)

        # 从磁盘中加载KNN模型
        with open('knn_model.pkl', 'rb') as file:
            knn = pickle.load(file)
        # 根据当前商品类型进行推荐
        recommendations = []
        if "categories" in current_goods:
            current_type = current_goods['categories']
            current_binary = mlb.transform([current_type])
            indices = knn.kneighbors(current_binary, n_neighbors=5, return_distance=False)
            for i in indices[0]:
                if data[i]['uid'] != current_goods['uid']:
                    recommendations.append(data[i]['uid'])
        return recommendations


recommend = Recommend()
if __name__ == '__main__':
    pass
