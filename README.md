# FurniFuture
FurniFuture is an intelligent home assistant for the blind. It helps to locate the furnitures in the space and can also find objects for the blind.
The system can be set up with common camera instead of special functionality cameras which brings great economic benefit. All actions are done using audio command and is very user-friendly to the blind. The project can also be extend to help the blind in the public space like school or station.
This project wins the second place in system-integration-and-implementation-group of [經濟部搶鮮大賽](https://www.getfresh.org.tw/achievement_detail.aspx?No=373).

## Project Structure
![](https://i.imgur.com/yrzosce.png)
### Server Side
The [Server Side code](https://github.com/mtbehisseste/FurniFuture/tree/master/tf-faster-rcnn) receives the realtime images taken from the camera set in the user's house. It then process the object detection and identification. It will also convert the position of the object to the first person sight for the blind, e.g. " The chair is three step from you in your right hand side. "
For object detection, we use [tf-faster-rcnn](https://github.com/endernewton/tf-faster-rcnn). Since data and models are too big so they are not uploaded here. Check out details for the project.
### User Side
User side includes [hand-hold devices](https://github.com/mtbehisseste/FurniFuture/tree/master/Speech) and [the camera](https://github.com/mtbehisseste/FurniFuture/tree/master/demo_computer). The hand-hold device receives the audio commands from the user and we use [Speech-to-Text](https://www.getfresh.org.tw/tdp_detail.aspx?No=288) from *ITRI(工研院)* to transfer the commands to text. It will send text command to the camera to take pictures. Then the camera sends pictures to the server to process object detection. After getting the result from the server, it convert the result from string to audio hint and speak out to the blind.

## SnapShots
![](https://i.imgur.com/LdMj46P.jpg?1)
![](https://i.imgur.com/XP0yFTR.jpg?1)
