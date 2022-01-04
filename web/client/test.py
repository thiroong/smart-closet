import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model


def get_test_data(input_size=(299, 299)):
    test_dir = 'static/datasets/test'
    test_datagen = ImageDataGenerator(rescale=1./255.)

    test_generator = test_datagen.flow_from_directory(test_dir,
                                                      batch_size=20,
                                                      class_mode='categorical',
                                                      target_size=input_size)
    return test_generator


def get_model(model_name):
    model_path = 'models'
    model = load_model(os.path.join(model_path, model_name))
    return model


def model_evaluate(model, test_data):
    loss, acc = model.evaluate(test_data, verbose=2)
    print("모델의 테스트 정확도: {:5.2f}%".format(100 * acc))


if __name__ == '__main__':
    test_data = get_test_data()
    cnn_model = get_model("c2c_cnn_model.h5")
    c2c_lc_model = get_model("c2c_ic_model.h5")
    c2c_ift_model = get_model("c2c_ift_model.h5")
    c2c_model = get_model("c2c_model.h5")

    print("====cnn model====")
    model_evaluate(cnn_model, test_data)
    print("====inception v3 classifier model====")
    model_evaluate(c2c_lc_model, test_data)
    print("====inception v3 fine tuning model====")
    model_evaluate(c2c_ift_model, test_data)
    print("====inception v3 classifier model2====")
    model_evaluate(c2c_model, test_data)

