# Local Environment Memory (MEMORY.md)

## Developer
- **Name**: Ken

## Workstation
- **OS**: Ubuntu 24.04 LTS
- **CPU**: Intel Core i7-8550U
- **RAM**: 16GB
- **GPU**: NVIDIA GTX970 4GB
- **Driver**: 535.309.01
- **CUDA Runtime**: 12.2

## Network
- **Router**: YAMAHA RTX1200
- **Developer PC**: `192.168.100.106`
- **ESP32 Camera**: `192.168.100.101`

## ESP32
- **Board**: Seeed XIAO ESP32S3 Sense
- **Required Build Flag**: `PSRAM=opi`
- **Arduino Core**: `esp32 3.3.10`

## Project Conventions
- **Logs**: `logs/`
- **Evidence**: `evidence_logs/`
- **Test Scripts**: `tests/`
- **Production Source**: `src/`

## Python Runtime
- **Python**: 3.11.9
- **Pyenv**: enabled
- **Virtual Environment**: project local

## AI Stack
- **Torch**: 2.5.1+cu121
- **CUDA**: 12.1
- **Ultralytics**: YOLOv8
- **OpenCV**: 4.11.0

## Known Issues
- **Torch Compatibility**: Torch CUDA 13 builds are incompatible with current driver.
- **Requirement**: Use `torch + cu121` exclusively.
