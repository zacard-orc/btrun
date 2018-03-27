#!/usr/bin/env bash
#proj_raw_name=`pwd`
#rm -Rf ./static/dist
#cp -r ../rp_web_admin/dist/ ./static/dist

rm -f *.log

proj_name="btrun"
tar --exclude='.git' \
--exclude='.idea' \
--exclude='*.log' \
--exclude='bit' \
--exclude='coincola' \
--exclude='*.xls' \
--exclude='ida' \
--exclude='policy' \
--exclude='tcp' \
--exclude='udp' \
--exclude='test' \
--exclude='./btrun.tar.gz' \
-zcvf $proj_name.tar.gz .

./code_scp.sh 47.96.10.189 wb tejwXPwZQ4FNx5AX05fv0XSAOMsEUL0xpF7cfSK6QJl6v $proj_name.tar.gz '~/btc'
#./code_scp.sh 106.15.193.49 wb tejwXPwZQ4FNx5AX05fv0XSAOMsEUL0xpF7cfSK6QJl6v $proj_name.tar.gz '~/btc'
#./code_scp.sh 120.27.216.222 wb tejwXPwZQ4FNx5AX05fv0XSAOMsEUL0xpF7cfSK6QJl6v $proj_name.tar.gz '~/btc'
./code_scp.sh 47.52.19.237 wb tejwXPwZQ4FNx5AX05fv0XSAOMsEUL0xpF7cfSK6QJl6v $proj_name.tar.gz '~/btc'
#./code_scp.sh 47.98.53.144 wb tejwXPwZQ4FNx5AX05fv0XSAOMsEUL0xpF7cfSK6QJl6v $proj_name.tar.gz '~/btc'

rm -f btrun.tar.gz


