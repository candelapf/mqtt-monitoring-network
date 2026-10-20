# Este material está protegido por la licencia CC BY-NC-SA 4.0.



# Copy VNX integration scenario XML
cp vnx-integracion.xml /usr/share/vnx/examples


# Destroy pending
cd /usr/share/vnx/examples
sudo vnx -f tutorial_lxc_ubuntu.xml -v --destroy
sudo vnx -f tutorial_lxc_ubuntu.xml -v --destroy


# Download container
cd /usr/share/vnx/filesystems
sudo vnx_download_rootfs -r vnx_rootfs_lxc_ubuntu64-20.04-v025.tgz -y -l

# Move to VNX examples directory
cd /usr/share/vnx/examples/

# Create the scenario
sudo vnx -f vnx-integracion.xml -v --create


# Setup the hosts dependencies
for host in `echo h2 h3`; do
    # Wait until internet connection is up
    down=1
    while [ $down -ne 0 ]; do
        echo Checking if $host has internet
        down=`sudo lxc-attach $host -- ping -c1 -W3 8.8.8.8 >/dev/null; echo $?`;
        sleep 1
    done


    # Install python dependencies for MQTT and pandas
    sudo lxc-attach $host apt update
    sudo lxc-attach $host -- apt install python3-pip -y
    sudo lxc-attach $host -- pip3 install paho-mqtt
    sudo lxc-attach $host -- pip3 install pandas
done

