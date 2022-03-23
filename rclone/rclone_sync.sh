#!/bin/sh
#sudo rclone sync -i /nas/gitea azure:gitea --config=rclone.conf --copy-links
sudo rclone sync /nas/gitea azure:gitea --config=rclone.conf --copy-links
