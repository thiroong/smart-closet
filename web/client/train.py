import os
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint


base_dir = '/static/datasets'

train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')


input_size = (299, 299)

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


inceptionV3 = InceptionV3(include_top=True)
base_inputs = inceptionV3.layers[0].input
base_outputs = inceptionV3.layers[-2].output
classifier = Dense(6, activation='softmax')(base_outputs)
inceptionV3_model = Model(inputs=base_inputs, outputs=classifier)

inceptionV3_model.compile(
    optimizer=Adam(),
    loss=tf.keras.losses.CategoricalCrossentropy(),
    metrics=["accuracy"]
)

early_stopping = EarlyStopping(monitor='val_loss', patience=15)

checkpoint_path = '/static/checkpoints/'
cb_checkpoint = ModelCheckpoint(os.path.join(checkpoint_path,
                                             'c2c_model.ckpt'),
                                save_weights_only=True,
                                monitor='val_loss',
                                verbose=1,
                                save_best_only=True)

inceptionV3_history = inceptionV3_model.fit(train_generator,
                                            validation_data=validation_generator,
                                            epochs=50,
                                            callbacks=[cb_checkpoint, early_stopping])

inceptionV3_model.save(os.path.join("/models", "c2c_model.h5"))