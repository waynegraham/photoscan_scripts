#! /usr/bin/env bash

unamestr=`uname`
photoscanpath=""
RENDER_MASTER="128.143.231.167"
ip=$(ifconfig | awk '/broadcast/{print $2}')

if [[ "$unamestr" == 'Linux' ]]; then
  photoscanpath=''
  network_share=''
elif [[ "$unamestr" == 'Darwin' ]]; then
  photoscanpath='/Applications/PhotoScanPro.app/Contents/MacOS/PhotoScanPro'
  network_share='/Volumes/lib_content66'
fi

#`$photoscanpath --node --dispatch --root $network_share $ip`

`$photoscanpath --node --dispatch $RENDER_MASTER`

