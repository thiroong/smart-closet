import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

clothes_info = {
    0: '0_coat', 1: '1_padding', 2: '2_shortsleeve',
    3: '3_longsleeve', 4: '4_shirt', 5: '5_pants', 6: '6_dress'
}

c2c_model = tf.keras.models.load_model('checkpoints/c2c_model.h5')


def rgba2rgb(rgba, background=(255,255,255)):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba
    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros((row, col, 3), dtype='float32')
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]
    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background
    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B

    return np.asarray( rgb, dtype='uint8' )


def get_test_image(path):
  image = tf.keras.load_img(path, color_mode='rgba', target_size=(299, 299))
  image = tf.keras.img_to_array(image)
  image = rgba2rgb(image)
  # image = image[80:-80, 80:-80]

  plt.imshow(image, interpolation='nearest')
  plt.show()

  image = np.expand_dims(image, axis=0)
  image = image.astype('float32')
  image = image / 255.0
  return image