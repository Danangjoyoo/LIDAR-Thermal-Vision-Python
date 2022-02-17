
echo "Installing ubuntu required apt packages"
sudo apt-get install -y curl build-essential checkinstall cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran python2-dev python3-dev python3-pip libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio


echo "Downloading OpenCV 4.4.0"
curl -L https://github.com/opencv/opencv/archive/4.4.0.zip -o opencv-4.4.0.zip
curl -L https://github.com/opencv/opencv_contrib/archive/4.4.0.zip -o opencv_contrib-4.4.0.zip
unzip opencv-4.4.0.zip
unzip opencv_contrib-4.4.0.zip

echo "Installing CUDA"
# It’s a bit tricky, you have to uninstall existing package manager
sudo apt remove --purge -y nvidia\*
sudo apt -y autoremove

# Then you have to disable nvidia noveau driver (link)
sudo bash -c "echo blacklist nouveau > /etc/modprobe.d/blacklist-nvidia-nouveau.conf"
sudo bash -c "echo options nouveau modeset=0 >> /etc/modprobe.d/blacklist-nvidia-nouveau.conf"

cat /etc/modprobe.d/blacklist-nvidia-nouveau.conf

sudo apt-get update
sudo apt update

echo "Installing CUDNN"
tar -xf ./cudnn-linux-x86_64-8.3.1.22_cuda11.5-archive.tar.xz
cd cudnn-linux-x86_64-8.3.1.22_cuda11.5-archive
sudo cp include/cudnn*.h /usr/local/cuda/include 
sudo cp -P lib/libcudnn* /usr/local/cuda/lib64 
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
cd ..

export PATH="/usr/local/cuda-11.5/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-11.5/lib64:$LD_LIBRARY_PATH"

echo "Building Package OpenCV 4.4.0"
cd opencv-4.4.0
mkdir build
cd build


cmake -D WITH_CUDA=ON \
-D CUDA_ARCH_BIN="5.0,5.3" \
-D CUDA_ARCH_PTX="" \
-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.4.0/modules \
-D BUILD_TESTS=OFF \
-D BUILD_PERF_TESTS=OFF \
-D BUILD_EXAMPLES=OFF \
-D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D BUILD_opencv_sfm=OFF \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_DNN_CUDA=ON \
-D WITH_CUBLAS=1 \
-D ENABLE_FAST_MATH=1 \
-D BUILD_NEW_PYTHON_SUPPORT=ON \
-D BUILD_opencv_python3=ON \
-D HAVE_opencv_python3=ON \
-D PYTHON_DEFAULT_EXECUTABLE=/usr/bin/python3.8 \
-D CUDA_FAST_MATH=1 ..

make -j6

echo "Installing OpenCV 4.4.0"
sudo checkinstall -D make install

gnome-terminal -- bash -c "echo '# setup debian package creation'; echo '1. Maintainer : admin@opencv.org'; echo '2. Summary : OpenCV 4.4.0 CUDA'; echo '3. Name : libopencv-4.4.0'; echo '4. Version : 4.4.0'; echo 'exit this once you complete OpenCV Installation'; exec bash"

sudo chmod 666 libopencv-4.4.0_4.4.0-1_amd64.deb
sudo mv libopencv-4.4.0_4.4.0-1_amd64.deb libopencv-4.4.0.deb
sudo dpkg --contents libopencv-4.4.0.deb

## install librealsense2 SDK
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u
sudo apt-get install -y librealsense2-dkms librealsense2-utils librealsense2-dev librealsense2-dbg
