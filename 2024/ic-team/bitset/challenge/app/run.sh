#!/bin/bash

cd /app || exit
export FLAG1='infobahn{fake_flag1}'
export FLAG2='infobahn{fake_flag2}'
export FLAG3='infobahn{fake_flag3}'
bun /app/server.js
