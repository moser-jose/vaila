#!/bin/bash

#########################################################################################
#                                                                                       #
# Script: install_vaila.linux.sh                                                        #
# Description: Installs the vaila - Multimodal Toolbox on Ubuntu Linux, including the   #
#              Conda environment setup, copying program files to the user's home        #
#              directory, creating a desktop entry, and setting up the application.     #
#                                                                                       #
# Usage:                                                                                #
#   1. Download the repository from GitHub manually and extract it.                     #
#   2. Make the script executable:                                                      #
#      chmod +x install_vaila.linux.sh                                                  #
#   3. Run the script from the root directory of the extracted repository:              #
#      ./install_vaila.linux.sh                                                         #
#                                                                                       #
# Notes:                                                                                #
#   - Ensure Conda is installed and accessible from the command line before running.    #
#                                                                                       #
# Author: Prof. Dr. Paulo R. P. Santiago                                                #
# Date: September 17, 2024                                                              #
# Version: 1.2                                                                          #
# OS: Ubuntu Linux                                                                      #
#########################################################################################

echo "Starting installation of vaila - Multimodal Toolbox on Linux..."

# Check if Conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed. Please install Conda first."
    exit 1
fi

# Get Conda base path
CONDA_BASE=$(conda info --base)

# Check if the "vaila" environment already exists
if conda env list | grep -q "^vaila"; then
    echo "Conda environment 'vaila' already exists. Updating it..."
    # Update the existing environment
    conda env update -n vaila -f yaml_for_conda_env/vaila_linux.yaml --prune
    if [ $? -eq 0 ]; then
        echo "'vaila' environment updated successfully."
    else
        echo "Failed to update 'vaila' environment."
        exit 1
    fi
else
    # Create the environment if it does not exist
    echo "Creating Conda environment from vaila_linux.yaml..."
    conda env create -f yaml_for_conda_env/vaila_linux.yaml
    if [ $? -eq 0 ]; then
        echo "'vaila' environment created successfully on Linux."
    else
        echo "Failed to create 'vaila' environment."
        exit 1
    fi
fi

# Check for NVIDIA GPU and install PyTorch with CUDA if available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Installing PyTorch with CUDA support..."
    conda install pytorch torchvision torchaudio pytorch-cuda -c pytorch -c nvidia -n vaila
    if [ $? -eq 0 ]; then
        echo "PyTorch with CUDA support installed successfully."
    else
        echo "Failed to install PyTorch with CUDA support."
    fi
else
    echo "No NVIDIA GPU detected. Skipping PyTorch with CUDA installation."
fi

# Define paths
USER_HOME="$HOME"
VAILA_HOME="$USER_HOME/vaila"
DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/vaila.desktop"

# Copy the entire vaila program to the user's home directory using cp -Rfa
echo "Copying vaila program to the user's home directory..."
mkdir -p "$VAILA_HOME"
cp -Rfa "$(pwd)/." "$VAILA_HOME/"

# Create a run_vaila.sh script
RUN_SCRIPT="$VAILA_HOME/run_vaila.sh"
echo "Creating run_vaila.sh script..."
cat <<EOF > "$RUN_SCRIPT"
#!/bin/bash
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate vaila
python3 "$VAILA_HOME/vaila.py"
EOF

# Make the run_vaila.sh script executable
chmod +x "$RUN_SCRIPT"

# Create a desktop entry for the application
echo "Creating a desktop entry for vaila..."
cat <<EOF > "$DESKTOP_ENTRY_PATH"
[Desktop Entry]
Version=1.0
Name=vaila
Comment=Multimodal Toolbox
Exec=$RUN_SCRIPT
Icon=$VAILA_HOME/docs/images/vaila.png
Terminal=false
Type=Application
Categories=Utility;
EOF

# Ensure the application directory is owned by the user and has the correct permissions
echo "Ensuring correct ownership and permissions for the application..."
chown -R "$USER:$USER" "$VAILA_HOME"
chmod -R u+rwX "$VAILA_HOME"
chmod +x "$RUN_SCRIPT"

# Remove ffmpeg from the Conda environment if installed
echo "Removing ffmpeg installed via Conda..."
conda remove -n vaila ffmpeg -y

# Install the system version of ffmpeg
echo "Installing ffmpeg from system repositories..."
sudo apt update
sudo apt install ffmpeg -y

# Activate the Conda environment
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate vaila

# Install moviepy using pip
echo "Installing moviepy..."
pip install moviepy

echo "vaila Launcher created and available in the Applications menu!"
echo "Installation and setup completed."
echo " "
