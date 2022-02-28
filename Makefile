.PHONY: all run models

MODEL_BASE_URI := https://argosopentech.nyc3.digitaloceanspaces.com/argospm

MODEL_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/model

MODELS := \
	translate-ar_en-1_0.argosmodel \
	translate-az_en-1_5.argosmodel \
	translate-zh_en-1_1.argosmodel \
	translate-cs_en-1_5.argosmodel \
	translate-nl_en-1_4.argosmodel \
	translate-en_ar-1_0.argosmodel \
	translate-en_az-1_5.argosmodel \
	translate-en_zh-1_1.argosmodel \
	translate-en_cs-1_5.argosmodel \
	translate-en_nl-1_4.argosmodel \
	translate-en_eo-1_5.argosmodel \
	translate-en_fi-1_5.argosmodel \
	translate-en_fr-1_0.argosmodel \
	translate-en_de-1_0.argosmodel \
	translate-en_el-1_5.argosmodel \
	translate-en_hi-1_1.argosmodel \
	translate-en_hu-1_5.argosmodel \
	translate-en_id-1_2.argosmodel \
	translate-en_ga-1_1.argosmodel \
	translate-en_it-1_0.argosmodel \
	translate-en_ja-1_1.argosmodel \
	translate-en_ko-1_1.argosmodel \
	translate-en_fa-1_5.argosmodel \
	translate-en_pl-1_1.argosmodel \
	translate-en_pt-1_0.argosmodel \
	translate-en_ru-1_1.argosmodel \
	translate-en_sk-1_5.argosmodel \
	translate-en_es-1_0.argosmodel \
	translate-en_sv-1_5.argosmodel \
	translate-en_tr-1_5.argosmodel \
	translate-en_uk-1_4.argosmodel \
	translate-en_vi-1_2.argosmodel \
	translate-eo_en-1_5.argosmodel \
	translate-fi_en-1_5.argosmodel \
	translate-fr_en-1_0.argosmodel \
	translate-de_en-1_0.argosmodel \
	translate-el_en-1_5.argosmodel \
	translate-hi_en-1_1.argosmodel \
	translate-hu_en-1_5.argosmodel \
	translate-id_en-1_2.argosmodel \
	translate-ga_en-1_1.argosmodel \
	translate-it_en-1_0.argosmodel \
	translate-ja_en-1_1.argosmodel \
	translate-ko_en-1_1.argosmodel \
	translate-fa_en-1_5.argosmodel \
	translate-pl_en-1_1.argosmodel \
	translate-pt_en-1_0.argosmodel \
	translate-ru_en-1_0.argosmodel \
	translate-sk_en-1_5.argosmodel \
	translate-es_en-1_0.argosmodel \
	translate-sv_en-1_5.argosmodel \
	translate-tr_en-1_5.argosmodel \
	translate-uk_en-1_4.argosmodel \
	translate-vi_en-1_2.argosmodel

MODEL_FILES := $(addprefix ${MODEL_DIR}/,${MODELS})

all:
	@echo 'Nothing to do - try `make models` or `make run`'

run:
	env TRANSLATION_MODEL_DIR="${MODEL_DIR}" python3 -m bellingbot

models: ${MODEL_FILES}

${MODEL_DIR}/%.argosmodel:
	@mkdir -p "$(dir $@)"
	curl -L "${MODEL_BASE_URI}/$(notdir $@)" > "$@"
