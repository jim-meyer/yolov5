# OBSOLETE: use od/voc_to_yolov5.py
#process_labels:
#	python3 utils.import_voc_labels

train_in_docker:
	# Dec2021 training
	#docker run -it -v $(PWD):/usr/src/app -v ~/ml:/ml ultralytics/yolov5:latest python3 train.py \
	#	--weights yolov5n6.pt --data data/trailcam_10_class_inc_background.yaml --cfg models/yolov5n.yaml --epochs 50 --freeze 10 --workers 0 --device cpu
	# Jan2022 training
	docker run -it -v $(PWD):/usr/src/app -v ~/ml:/ml ultralytics/yolov5:latest python3 train.py \
		--weights yolov5n6.pt --data data/trailcam_10_class_jan_2022.yaml --cfg models/yolov5n.yaml --epochs 50 --freeze 10 --workers 0 --device cpu

enter_container:
	docker run -it \
		-v $(PWD):/usr/src/app \
		-v ~/tmp/yolov5:/yolov5/data \
		-v ~/models:/models \
		-v ~/ml:/ml \
		yolov5_yolov5:latest /bin/bash

detect_nov_2021_model:
	find ${IMAGES_DIR} -name *.JPG -exec chmod ugo-w {} + && \
	docker run -it \
		-v $(PWD):/usr/src/app \
		-v ~/tmp/yolov5:/yolov5/data \
		-v ~/models:/models \
		-v ~/tmp:/hosttmp \
		-v ${IMAGES_DIR}:/trailcam_picts \
		yolov5_yolov5:latest \
		python3 detect.py \
		--weights /models/trailcam/yolov5/original_mar_may_nov_nov2_dec_2020_feb_mar_2021/exp32/weights/best.pt \
		--source '/trailcam_picts/*.JPG' \
		--save-txt \
		--output-dir /trailcam_picts
# Don't need to save as VOC since LabelImg handles YOLO .txt label files fine. And we want to preserve the original predicted labels anyway.
# 	--save-voc --voc-ext ._xml --classes Bobcat Coyote Deer DeerBuck DeerDoe Possum Rabbit Raccoon Squirrel Turkey \


detect_dec_2021_model:
	docker run -it \
		-v $(PWD):/usr/src/app \
		-v ~/tmp/yolov5:/yolov5/data \
		-v ~/models:/models \
		-v ~/tmp:/hosttmp \
		-v ${IMAGES_DIR}:/trailcam_picts \
		yolov5_yolov5:latest \
		python3 detect.py \
		--weights /models/trailcam/yolov5/trailcam_picts_original_mar_may_nov_nov2_dec_2020_feb_mar_apr_may_dec_2021/exp35/weights/best.pt \
		--source '/trailcam_picts/*.[jJ][pP][gG]' \
		--save-txt \
		--output-dir /trailcam_picts
