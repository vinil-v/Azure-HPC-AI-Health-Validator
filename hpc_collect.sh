#!/bin/bash
# HPC Health Collector for Microsoft Support Hackathon
LOG_FILE="gpu_diag_$(hostname).log"

echo "=== START NVIDIA-SMI XML ===" > $LOG_FILE
# The -x flag is critical for the Python XML parser
nvidia-smi -q -x >> $LOG_FILE 2>&1
echo "=== END NVIDIA-SMI XML ===" >> $LOG_FILE

echo "=== START IBSTATUS ===" >> $LOG_FILE
ibstatus >> $LOG_FILE 2>&1
echo "=== END IBSTATUS ===" >> $LOG_FILE

echo "=== START DMESG ===" >> $LOG_FILE
dmesg | grep -iE "NVRM|XID|NVLink" | tail -n 50 >> $LOG_FILE 2>&1
echo "=== END DMESG ===" >> $LOG_FILE

echo "Done! Collected GPU diagnostics in $LOG_FILE"