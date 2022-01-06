import os
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


def get_data(input_size=(299, 299)):
    '''
        [argument]
            input_size              : [tuple] [default=(299, 299)]
                                    모델에 사용할 입력 사이즈 (사진 shape)
        [action]
                                    : ImageDataGenerator를 사용하여 train, valid, test set를 만드는 작업 수행
                                    (비율은 0.7, 0.2, 0.1로 디렉토리에 이미 저장되어 있음.)
                                    Data Augmentation 방법은 회전, 상하좌우 옮기기 등의 작업 수행
                                    (모델의 입력에 맞는 전처리 수행)
        [return]
            train_generator         : [ImageDataGenerator] train set
            validation_generator    : [ImageDataGenerator] validation set
            test_generator          : [ImageDataGenerator] test set
    '''
    base_dir = 'static/datasets'
    train_dir = os.path.join(base_dir, 'train')
    validation_dir = os.path.join(base_dir, 'validation')
    test_dir = os.path.join(base_dir, 'test')

    train_datagen = ImageDataGenerator(rescale=1./255.,
                                       rotation_range=40,
                                       width_shift_range=0.2,
                                       height_shift_range=0.2,
                                       shear_range=0.2,
                                       zoom_range=0.2,
                                       horizontal_flip=True)
    test_datagen = ImageDataGenerator(rescale=1./255.)

    train_generator = train_datagen.flow_from_directory(train_dir,
                                                        batch_size=20,
                                                        class_mode='categorical',
                                                        target_size=input_size)
    validation_generator = train_datagen.flow_from_directory(validation_dir,
                                                             batch_size=20,
                                                             class_mode='categorical',
                                                             target_size=input_size)
    test_generator = test_datagen.flow_from_directory(test_dir,
                                                      batch_size=20,
                                                      class_mode='categorical',
                                                      target_size=input_size)
    return train_generator, validation_generator, test_generator


# cpu 사용 시 한 epoch 당 45~60s
# colab gpu 사용 시 한 epoch 당 23s~26s
def basic_cnn_model():
    '''
        [argument]

        [action]
                                    : cnn 모델 구조를 쌓고 cnn 모델을 반환
        [return]
            basic_cnn_model         : [tf.keras Model] cnn 모델 반환
    '''
    basic_cnn_model = Sequential()
    basic_cnn_model.add(Conv2D(32, (3,3), activation='relu', input_shape=(299, 299, 3)))
    basic_cnn_model.add(MaxPooling2D(2,2))
    basic_cnn_model.add(Conv2D(64, (3,3), activation='relu'))
    basic_cnn_model.add(MaxPooling2D(2,2))
    basic_cnn_model.add(Conv2D(64, (3,3), activation='relu'))
    basic_cnn_model.add(Flatten())
    basic_cnn_model.add(Dense(7, activation='softmax'))
    return basic_cnn_model


# cpu 사용 시 한 epoch 당 240~260s
def inceptionV3_classifier():
    '''
        [argument]

        [action]
                                    : imageNet 데이터를 활용하여 pre-train된 inception V3 모델을 로드하고
                                    Transfer learning을 위해 classifier 부분을 제외한 다른 레이어의 weights를 고정하고,
                                    classifier 부분을 새로운 task에 맞는 새로운 classifier로 교체한 모델을 반환
        [return]
            inceptionV3_model         : [tf.keras Model] inceptionV3 transfer learning 모델 반환
    '''
    inceptionV3 = InceptionV3(weights='imagenet', input_shape=(299, 299, 3))
    base_inputs = inceptionV3.layers[0].input
    base_outputs = inceptionV3.layers[-2].output
    classifier = Dense(7, activation='softmax')(base_outputs)
    inceptionV3_model = Model(inputs=base_inputs, outputs=classifier)
    return inceptionV3_model


# cpu 사용 시 한 epoch 당 240~260s
def inceptionV3_fine_tunning():
    '''
        [argument]

        [action]
                                    : imageNet 데이터를 활용하여 pre-train된 inception V3 모델을 로드하여
                                    Transfer learning과 fine tuning을 위해 전체 모델 구조를 학습가능하게 하고,
                                    classifier 부분을 새로운 task에 맞는 새로운 classifier로 교체한 모델을 반환
        [return]
            inceptionV3_ft_model         : [tf.keras Model] inceptionV3 transfer learning + fine-tuning 모델 반환
    '''
    inception_V3 = InceptionV3(weights='imagenet', input_shape=(299, 299, 3))
    for layer in inception_V3.layers[:]:
        layer.trainable = True
    base_inputs = inception_V3.layers[0].input
    base_outputs = inception_V3.layers[-2].output
    classifier = tf.keras.layers.Dense(7, activation='softmax')(base_outputs)
    inceptionV3_ft_model = tf.keras.Model(inputs=base_inputs, outputs=classifier)

    return inceptionV3_ft_model


def c2c_model_features(c2c_model):
    '''
        [argument]
            c2c_model       : [tf.keras Model] 옷 이미지 분류에 사용한 Model
        [action]
                            : 마지막 classifier의 입력 자체를 유사도 측정에 사용하기 위해
                            마지막 classifier 를 제외한 모델 반환
        [return]
            extract_model   : [tf.keras Model] c2c_model의 classifier 부분을 제외한 모델 반환
    '''
    base_inputs = c2c_model.layers[0].input
    base_outputs = c2c_model.layers[-2].output
    extract_model = Model(inputs=base_inputs, outputs=base_outputs)
    extract_model.save(os.path.join("models", "c2c_extraction_model.h5"))
    return extract_model


def train_model(model, name, train_generator, validation_generator):
    '''
        [argument]
            model                   : [tf.keras Model] 옷 이미지 분류에 학습할 Model
            name                    : [string] 모델의 이름 (ex: cnn, ic(inceptionV3 classifier), ift(inceptionV3 fine tuning))
            train_generator         : [tf.keras ImageDataGenerator] train data
            validation_generator    : [tf.keras ImageDataGenerator] validation data
        [action]
                            : 모델 학습 및 저장
        [return]
    '''
    model.compile(loss=CategoricalCrossentropy(),
                              optimizer=Adam(),
                              metrics=["accuracy"])

    early_stopping = EarlyStopping(monitor='val_loss', patience=17)

    checkpoint_path = 'static/checkpoints/'
    cb_checkpoint = ModelCheckpoint(os.path.join(checkpoint_path,
                                                 'c2c_{name}_model.ckpt'.format(name=name)),
                                    save_weights_only=True,
                                    monitor='val_loss',
                                    verbose=1,
                                    save_best_only=True)

    model_history = model.fit(train_generator,
                              validation_data=validation_generator,
                              epochs=100,
                              callbacks=[cb_checkpoint, early_stopping])

    model.save(os.path.join("models", "c2c_{name}_model.h5".format(name=name)))


if __name__ == '__main__':
    train, valid, test = get_data()
    cnn_model = basic_cnn_model()
    inceptionV3_clas = inceptionV3_classifier()
    inceptionV3_fine = inceptionV3_fine_tunning()
    train_model(cnn_model, "cnn", train, valid)
    train_model(inceptionV3_clas, "ic", train, valid)
    train_model(inceptionV3_fine, "ift", train, valid)
    extract_model = c2c_model_features(inceptionV3_clas)

    # from tensorflow.keras.models import load_model
    # c2c_model = load_model('models/c2c_model.h5')
    # extract_model = c2c_model_features(c2c_model)

