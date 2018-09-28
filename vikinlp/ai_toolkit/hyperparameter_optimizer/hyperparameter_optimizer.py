import tensorflow as tf

from vikinlp.classifier import dl_model
from vikinlp.ai_toolkit.util import zh


def search_lr():
    zh.set_chinese_font()
    parameter = parameter_definition()

    dl_model.tf_train_model(parameter)


def parameter_definition():
    flags = tf.flags
    # 嵌入式向量维度
    flags.DEFINE_integer('embedding_dim', 300,
                         'Dimensionality of embedding (default: 128)')
    # 卷积核结构
    flags.DEFINE_string('filter_sizes', '3,4,5',
                        'Comma-separated filter sizes (default: "3,4,5")')
    # 卷积层中卷积核个数
    flags.DEFINE_integer('num_filters', 128,
                         'Number of filters per filter size (default: 128)')
    # Dropout率
    flags.DEFINE_float('dropout_keep_prob', 0.5,
                       'Dropout keep probability (default: 0.5)')
    # l2正则系数
    flags.DEFINE_float('l2_reg_lambda', 0.0,
                       'L2 regularization lambda (default: 0.0)')

    # 学习率
    # dic_lr = {"learning_rate": 1e-5, "max_lr": 0.1, "step_size": 384, "mode": 'triangular2'}
    flags.DEFINE_list('lr', [1e-5, 0.1, 384, "triangular2"], 'Learning Rate (default: 1e-3)')

    # 批次大小
    flags.DEFINE_integer('batch_size', 64, 'Batch Size (default: 64)')
    # epoch次数
    flags.DEFINE_integer('num_epochs', 10,
                         'Number of training epochs (default: 10)')
    # 多少个样本进行一次评价
    flags.DEFINE_integer(
        'evaluate_every', 100,
        'Evaluate model on dev set after this many steps (default: 100)')

    # 每100步保存一次
    flags.DEFINE_integer('checkpoint_every', 100,
                         'Save model after this many steps (default: 100)')
    # 不分好坏就是保存最后的num_checkpoints个模型
    flags.DEFINE_integer('num_checkpoints', 5,
                         'Number of checkpoints to store (default: 5)')
    # 其他参数
    # =====
    # allow_soft_placement: 获取到 operations 和 Tensor
    # 被指派到哪个设备(几号CPU或几号GPU)上运行,会在终端打印出各项操作是在哪个设备上运行
    flags.DEFINE_boolean('allow_soft_placement', True,
                         'Allow device soft device placement')
    # log_device_placement: 允许tf自动选择一个存在并且可用的设备来运行操作，
    # 在多个CPU或GPU设备的时候很有用
    flags.DEFINE_boolean('log_device_placement', False,
                         'Log placement of ops on devices')

    FLAGS = flags.FLAGS
    dict_parameter = FLAGS.flag_values_dict()
    print('\nParameters:')
    for item in dict_parameter:
        print('{}={}'.format(item, dict_parameter[item]))
    return FLAGS


if __name__ == '__main__':
    search_lr()