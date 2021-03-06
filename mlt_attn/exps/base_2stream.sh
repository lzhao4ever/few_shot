CUR_DIR=$(pwd)

MODEL=base_2stream
EXP_NAME=${MODEL}
MODEL_PATH=models/$EXP_NAME.pth
TENSORBOARD_PATH=tensorboard/$EXP_NAME
LOG_PATH=logs/$EXP_NAME.log
FIG_PATH=figures/$EXP_NAME
BATCH_SIZE=32
IMAGE_SIZE=256
NUM_SCALE=1
NUM_CLASS=6

cd ..

## Train
CUDA_VISIBLE_DEVICES=1 python main.py --train --exp_name=$EXP_NAME --data=mlt --model=$MODEL --batch_size=$BATCH_SIZE --image_size=$IMAGE_SIZE --num_scale=$NUM_SCALE --num_class=$NUM_CLASS --show_statistics=basic --save_model_path=$MODEL_PATH --tensorboard_path=$TENSORBOARD_PATH |& tee $LOG_PATH

## Test
CUDA_VISIBLE_DEVICES=1 python main.py --test --exp_name=$EXP_NAME --data=mlt --model=$MODEL --batch_size=$BATCH_SIZE --image_size=$IMAGE_SIZE --num_scale=$NUM_SCALE --num_class=$NUM_CLASS --show_statistics=basic --init_model_path=$MODEL_PATH |& tee -a $LOG_PATH

cd $CUR_DIR
